"""
image_maker.py
Generates a premium 16:9 banner using GEMINI_IMAGE_API_KEY (separate from analysis key).
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
    """Simple PIL banner used only when Gemini API fails."""
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
    Generate premium 16:9 banner via Gemini image generation.
    Uses GEMINI_IMAGE_API_KEY (separate from tool analysis key).
    Falls back to PIL on any failure.
    """
    try:
        from google import genai
        from google.genai import types
        from config import GEMINI_IMAGE_API_KEY

        # Use dedicated image API key
        client = genai.Client(api_key=GEMINI_IMAGE_API_KEY)

        image_prompt = f"""Create a premium minimal 16:9 banner with a soft modern UI design.

Background:
- Very subtle grid pattern (5% opacity) on a near-white (#F7F8FA) surface
- Smooth soft blur glow shape in top-left corner (light blue-purple, very faint)
- Light grain texture (2%) for premium feel

Main Card:
- Centered glassmorphism card, wide proportions for 16:9 layout
- Rounded corners (24px)
- Soft layered shadow
- Subtle border 1px rgba(0,0,0,0.05)
- Top light reflection gradient strip

Content — ONLY TWO ELEMENTS, perfectly centered inside card:
1. Title (BIG, BOLD):
   {emoji} {tool_name}
2. Description (below title, clean spacing, soft color #555555):
   {short_description}

Typography:
- Font: Inter / Poppins / Satoshi — clean modern sans-serif
- Title: Very bold, large, color #111111
- Description: Medium weight, smaller, color #555555
- Perfect centering inside the card

Design Style:
- Ultra minimal, Apple / Notion aesthetic
- Clean negative space
- NO price badge, NO score, NO links, NO extra labels, NO watermark

Extra:
- Very subtle purple-blue glow behind the title text
- Smooth lighting from top-left
- High resolution, sharp, premium finish

Aspect Ratio: exactly 16:9"""

        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
                if img.size != (1920, 1080):
                    img = img.resize((1920, 1080), Image.LANCZOS)
                out = "temp_card.png"
                img.save(out, "PNG", quality=100)
                logger.info(f"Gemini image generated: {out}")
                return out

        logger.warning("No image in Gemini response — using PIL fallback")
        return _pil_fallback(tool_name, short_description, emoji)

    except Exception as e:
        logger.error(f"Gemini image generation failed: {e} — using PIL fallback")
        return _pil_fallback(tool_name, short_description, emoji)
