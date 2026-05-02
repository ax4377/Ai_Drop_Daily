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
# PIL fallback helpers
# ─────────────────────────────────────────────

def get_font(size, bold=False):
    paths = (
        [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
        if bold else
        [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    )
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, r, fill=None, outline=None, width=1):
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle(xy, fill=fill, outline=outline, width=width)


def _pil_fallback(tool_name, short_description, emoji):
    """PIL banner — used only when Gemini API fails."""
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (247, 248, 250, 255))
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 72):
        draw.line([(x, 0), (x, H)], fill=(0, 0, 0, 13), width=1)
    for y in range(0, H, 72):
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, 13), width=1)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-350, -350, 950, 750], fill=(195, 210, 255, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    img = Image.alpha_composite(img, glow)

    grain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grain)
    for _ in range(19200):
        gd.point((random.randint(0, W-1), random.randint(0, H-1)),
                 fill=(0, 0, 0, random.randint(8, 18)))
    img = Image.alpha_composite(img, grain)

    cw, ch = 1120, 540
    cx_off = (W - cw) // 2
    cy_off = (H - ch) // 2
    for s_off, s_blur, s_alpha in [(38, 55, 14), (12, 22, 9)]:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_rounded_rect(ImageDraw.Draw(sh),
                          [cx_off, cy_off+s_off, cx_off+cw, cy_off+ch+s_off],
                          28, fill=(0, 0, 0, s_alpha))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(s_blur)))

    card_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(card_l),
                      [cx_off, cy_off, cx_off+cw, cy_off+ch],
                      28, fill=(255, 255, 255, 230), outline=(0, 0, 0, 13), width=1)
    img = Image.alpha_composite(img, card_l)

    fd = ImageDraw.Draw(img)
    cx = W // 2
    title_font = get_font(86, bold=True)
    desc_font  = get_font(42, bold=False)

    title_text = f"{emoji}  {tool_name}"
    try:
        tw = fd.textbbox((0, 0), title_text, font=title_font)[2]
    except Exception:
        tw = 600
    title_y = cy_off + ch // 2 - 90

    gt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gt).text((cx - tw//2, title_y), title_text,
                            fill=(90, 110, 255, 36), font=title_font)
    img = Image.alpha_composite(img, gt.filter(ImageFilter.GaussianBlur(14)))

    fd = ImageDraw.Draw(img)
    fd.text((cx - tw//2, title_y), title_text, fill=(17, 17, 17), font=title_font)

    max_w = cw - 180
    words = short_description.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        try:
            lw = fd.textbbox((0, 0), test, font=desc_font)[2]
        except Exception:
            lw = len(test) * 23
        if lw <= max_w:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    for i, ln in enumerate(lines[:2]):
        try:
            lw = fd.textbbox((0, 0), ln, font=desc_font)[2]
        except Exception:
            lw = 300
        fd.text((cx - lw//2, title_y + 120 + i * 58), ln,
                fill=(85, 85, 85), font=desc_font)

    wm_font = get_font(28)
    wm = "AI Drop Daily"
    try:
        ww = fd.textbbox((0, 0), wm, font=wm_font)[2]
    except Exception:
        ww = 150
    fd.text((cx - ww//2, H - 46), wm, fill=(190, 190, 190), font=wm_font)

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

        image_prompt = f"""A premium minimal 16:9 UI banner design for a tech/AI product announcement.

Background: near-white (#F7F8FA) surface, very subtle dot grid pattern at 5% opacity, soft blue-purple glow blob in top-left corner, tiny grain texture for premium feel.

Center: a large glassmorphism card — white semi-transparent fill, rounded corners (24px), soft multi-layer drop shadow, 1px light border, thin top highlight strip simulating glass reflection.

Inside the card — ONLY these two text elements, perfectly centered:
1. Large bold title: "{emoji} {tool_name}" — dark #111111, with a very subtle purple glow behind it
2. Below the title with generous spacing, description in medium weight smaller font, color #555555: "{short_description}"

Style: ultra minimal Apple/Notion aesthetic, generous negative space, no icons, no badges, no extra decorations, no price, no rating, no watermark, no extra labels.

Overall feel: high-end SaaS product card, sharp, clean, premium finish."""

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

        # Extract image — skip thought parts
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
        return _pil_fallback(tool_name, short_description, emoji)

    except Exception as e:
        logger.error(f"Gemini image generation failed: {e} — using PIL fallback")
        return _pil_fallback(tool_name, short_description, emoji)
