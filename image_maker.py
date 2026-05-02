"""
image_maker.py
Generates a premium 16:9 banner using Gemini image generation API.
Model: gemini-3.1-flash-image-preview (Google AI Studio compatible)
Falls back to PIL if API call fails.
"""
import logging
import os
import random
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Font loader — Poppins preferred
# ─────────────────────────────────────────────

def get_font(size, style="regular"):
    font_map = {
        "bold":    [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        "medium":  [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
        "regular": [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
        "light":   [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
    }
    for path in font_map.get(style, font_map["regular"]):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, r, fill=None, outline=None, width=1):
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle(xy, fill=fill, outline=outline, width=width)


# ─────────────────────────────────────────────
# PIL fallback — clean flat Apple-style banner
# ─────────────────────────────────────────────

def _pil_fallback(tool_name, short_description, emoji=None):
    """
    Premium 16:9 banner — Poppins, flat text, no emoji, no 3D shadows.
    Apple keynote / Notion style.
    """
    W, H = 1920, 1080

    # Background: light cool gray
    img = Image.new("RGBA", (W, H), (235, 237, 242, 255))

    # Subtle grid
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 60):
        gd.line([(x, 0), (x, H)], fill=(170, 175, 195, 30), width=1)
    for y in range(0, H, 60):
        gd.line([(0, y), (W, y)], fill=(170, 175, 195, 30), width=1)
    img = Image.alpha_composite(img, grid)

    # Bottom-right soft curve glow
    br_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(br_glow).ellipse([W-700, H-550, W+350, H+250], fill=(215, 218, 232, 60))
    br_glow = br_glow.filter(ImageFilter.GaussianBlur(130))
    img = Image.alpha_composite(img, br_glow)

    # Card shadow layers (depth, not 3D text)
    card_w, card_h = 1140, 600
    card_x = (W - card_w) // 2
    card_y = (H - card_h) // 2 - 10

    for s_off, s_blur, s_alpha in [(50, 80, 16), (20, 35, 10), (8, 16, 7)]:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_rounded_rect(ImageDraw.Draw(sh),
            [card_x+10, card_y+s_off, card_x+card_w-10, card_y+card_h+s_off],
            32, fill=(140, 145, 165, s_alpha))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(s_blur)))

    # Card body
    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(card_layer),
        [card_x, card_y, card_x+card_w, card_y+card_h],
        32, fill=(251, 252, 254, 250))
    img = Image.alpha_composite(img, card_layer)

    # ── Typography — flat, no shadow, no emoji ──
    fd = ImageDraw.Draw(img)
    cx = W // 2
    card_cy = card_y + card_h // 2

    # Title — big, bold, flat
    title_font = get_font(112, "bold")
    try:
        tw = fd.textbbox((0, 0), tool_name, font=title_font)[2]
    except Exception:
        tw = 700
    title_y = card_cy - 110
    fd.text((cx - tw // 2, title_y), tool_name, fill=(26, 26, 26), font=title_font)

    # Description — flat, centered, gray
    desc_font = get_font(46, "regular")
    desc_color = (105, 107, 115)

    max_w = card_w - 200
    words = short_description.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        try:
            lw = fd.textbbox((0, 0), test, font=desc_font)[2]
        except Exception:
            lw = len(test) * 25
        if lw <= max_w:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    lines = lines[:2]

    desc_y = title_y + 155
    for i, ln in enumerate(lines):
        try:
            lw = fd.textbbox((0, 0), ln, font=desc_font)[2]
        except Exception:
            lw = 400
        fd.text((cx - lw // 2, desc_y + i * 64), ln, fill=desc_color, font=desc_font)

    img = img.convert("RGB")
    out = "temp_card.png"
    img.save(out, "PNG", quality=100)
    logger.info("PIL fallback banner saved.")
    return out


# ─────────────────────────────────────────────
# Main — Gemini image generation
# ─────────────────────────────────────────────

def create_tool_card(tool_name, short_description, price_type, emoji, score):
    """
    Generate premium 16:9 banner via gemini-3.1-flash-image-preview.
    Uses GEMINI_IMAGE_API_KEY — separate from tool analysis key.
    Falls back to PIL on any failure.
    """
    try:
        from google import genai
        from google.genai import types
        from config import GEMINI_IMAGE_API_KEY

        client = genai.Client(api_key=GEMINI_IMAGE_API_KEY)

        image_prompt = f"""A premium minimal 16:9 UI banner — Apple keynote / Notion style.

Background: light cool gray (#EBEDF2), subtle dot grid at low opacity, soft glow blob bottom-right corner.

Center: a large rounded card (radius 32px), very light white fill (#FBFCFE), soft multi-layer drop shadow for depth.

Inside the card — ONLY these two text elements, perfectly centered:
1. Title (large, bold, Poppins/SF Pro style, flat — NO 3D, NO shadow, NO emoji):
   {tool_name}
2. Description (below title, regular weight, smaller, flat, color #696B73):
   {short_description}

Rules:
- NO emoji anywhere
- NO 3D effect, NO text shadow, NO glow on text
- NO price, NO score, NO badge, NO watermark
- Clean negative space, ultra minimal
- Sharp, high resolution, premium finish

Aspect ratio: 16:9"""

        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                    image_size="2K",
                ),
            )
        )

        for part in response.parts:
            if getattr(part, 'thought', False):
                continue
            if part.inline_data is not None:
                img = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
                out = "temp_card.png"
                img.save(out, "PNG", quality=100)
                logger.info(f"Gemini image generated successfully: {out}")
                return out

        logger.warning("No image in Gemini response — using PIL fallback")
        return _pil_fallback(tool_name, short_description)

    except Exception as e:
        logger.error(f"Gemini image generation failed: {e} — using PIL fallback")
        return _pil_fallback(tool_name, short_description)
