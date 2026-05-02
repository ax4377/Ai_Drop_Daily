"""
image_maker.py
Generates a premium 16:9 banner using PIL only.
Fonts are bundled in ./fonts/ folder — works on Railway too.
"""
import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Font paths — bundled fonts folder (Railway compatible)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD    = os.path.join(BASE_DIR, "fonts", "Poppins-Bold.ttf")
FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "Poppins-Regular.ttf")

# System font fallbacks (always available on Linux/Railway)
SYSTEM_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SYSTEM_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def get_font(size, style="regular"):
    # 1. Try bundled Poppins first
    path = FONT_BOLD if style == "bold" else FONT_REGULAR
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    # 2. System font fallback (proper TTF — correct bbox calculations)
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


def create_tool_card(tool_name, short_description, price_type, emoji, score):
    """
    Generate premium 16:9 banner using PIL + bundled Poppins fonts.
    Apple keynote / Notion style — flat text, no emoji, no 3D.
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

    # Bottom-right soft glow
    br_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(br_glow).ellipse([W-700, H-550, W+350, H+250], fill=(215, 218, 232, 60))
    br_glow = br_glow.filter(ImageFilter.GaussianBlur(130))
    img = Image.alpha_composite(img, br_glow)

    # Card shadow layers
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

    fd = ImageDraw.Draw(img)
    cx = W // 2
    card_cy = card_y + card_h // 2

    # Title — big, bold, flat
    title_font = get_font(112, "bold")
    title_bbox = fd.textbbox((0, 0), tool_name, font=title_font)
    tw      = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    # Description font & line wrapping (do this BEFORE placing title
    # so we know total block height and can centre everything)
    desc_font  = get_font(46, "regular")
    desc_color = (105, 107, 115)
    line_gap   = 72  # px between description lines

    max_w = card_w - 200
    words = short_description.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        lw = fd.textbbox((0, 0), test, font=desc_font)[2]
        if lw <= max_w:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    lines = lines[:2]

    desc_h = len(lines) * line_gap  # total height of desc block

    # --- Vertical spacing ---
    # Gap between title-bottom and description-top
    GAP = 60   # <-- tweak this value to control title↔desc spacing

    # Total content height
    total_h = title_h + GAP + desc_h

    # Start y so the whole block is vertically centred in the card
    block_start_y = card_cy - total_h // 2

    title_y = block_start_y
    desc_y  = title_y + title_h + GAP

    # Draw title
    fd.text((cx - tw // 2, title_y), tool_name, fill=(26, 26, 26), font=title_font)

    # Draw description lines
    for i, ln in enumerate(lines):
        lw = fd.textbbox((0, 0), ln, font=desc_font)[2]
        fd.text((cx - lw // 2, desc_y + i * line_gap), ln, fill=desc_color, font=desc_font)

    img = img.convert("RGB")
    out = "temp_card.png"
    img.save(out, "PNG", quality=100)
    logger.info(f"Banner created: {out}")
    return out
