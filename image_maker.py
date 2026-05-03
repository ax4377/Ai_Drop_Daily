"""
image_maker.py
Generates an ultra-minimal premium 16:9 banner based on Apple-style UI.
"""
import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: In fonts ko use karne ke liye aapko ye files fonts/ folder mein rakhni hongi.
FONT_BOLD    = os.path.join(BASE_DIR, "fonts", "Satoshi-Bold.ttf")
FONT_MEDIUM  = os.path.join(BASE_DIR, "fonts", "Satoshi-Medium.ttf")

SYSTEM_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SYSTEM_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def get_font(size, style="bold"):
    path = FONT_BOLD if style == "bold" else FONT_MEDIUM
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    sys_path = SYSTEM_BOLD if style == "bold" else SYSTEM_REGULAR
    if os.path.exists(sys_path):
        try:
            return ImageFont.truetype(sys_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_rounded_rect(draw, xy, r, fill=None, outline=None, width=1):
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle(xy, fill=fill, outline=outline, width=width)

def create_tool_card(tool_name, short_description, watermark="@Ai_Drop_Daily"):
    W, H = 1920, 1080

    # ── Background (Clean Light Gray) ───────────────────────────
    img = Image.new("RGBA", (W, H), (242, 244, 247, 255))

    # Ultra-subtle grid
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    grid_spacing = 60
    for x in range(0, W, grid_spacing):
        gd.line([(x, 0), (x, H)], fill=(200, 205, 220, 15), width=1)
    for y in range(0, H, grid_spacing):
        gd.line([(0, y), (W, y)], fill=(200, 205, 220, 15), width=1)
    img = Image.alpha_composite(img, grid)

    # ── Card Dimensions ─────────────────────────────────────────
    card_w, card_h = 1200, 640
    card_x = (W - card_w) // 2
    card_y = (H - card_h) // 2

    # Simple Soft Shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(shadow),
        [card_x+5, card_y+15, card_x+card_w-5, card_y+card_h+25],
        60, fill=(0, 0, 0, 12))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(30)))

    # Main White Card (Frosted Look)
    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(card_layer),
        [card_x, card_y, card_x+card_w, card_y+card_h],
        60, fill=(255, 255, 255, 250))
    img = Image.alpha_composite(img, card_layer)

    fd = ImageDraw.Draw(img)
    cx = W // 2

    # ── Typography (Satoshi/Inter Style) ────────────────────────
    title_font = get_font(160, "bold")    # Large Bold Title
    desc_font  = get_font(58, "medium")   # Clean Medium Subtitle
    GAP = 45                               # Tight spacing for modern look

    # ── Layout Calculation ──────────────────────────────────────
    t_bbox  = fd.textbbox((0, 0), tool_name, font=title_font)
    title_w = t_bbox[2] - t_bbox[0]
    title_h = t_bbox[3] - t_bbox[1]

    d_bbox  = fd.textbbox((0, 0), short_description, font=desc_font)
    desc_w  = d_bbox[2] - d_bbox[0]
    desc_h  = d_bbox[3] - d_bbox[1]

    total_content_h = title_h + GAP + desc_h
    content_start_y = card_y + (card_h - total_content_h) // 2 - 20

    # ── Draw Text ───────────────────────────────────────────────
    # Title
    fd.text((cx - title_w // 2, content_start_y), tool_name,
            fill=(0, 0, 0), font=title_font)

    # Subtitle
    fd.text((cx - desc_w // 2, content_start_y + title_h + GAP), short_description,
            fill=(30, 30, 30), font=desc_font)

    # Watermark (Bottom Center)
    wm_font = get_font(32, "medium")
    wm_w = fd.textbbox((0, 0), watermark, font=wm_font)[2]
    fd.text((cx - wm_w // 2, H - 70), watermark, fill=(180, 185, 200), font=wm_font)

    # ── Save ────────────────────────────────────────────────────
    img = img.convert("RGB")
    out = "modern_ui_card.png"
    img.save(out, "PNG", quality=100)
    logger.info(f"Design Updated: {out}")
    return out

# Example Usage:
# create_tool_card("ChatGPT", "The most powerful AI chatbot for writing, coding & more")
