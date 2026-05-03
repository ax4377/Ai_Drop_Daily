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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD    = os.path.join(BASE_DIR, "fonts", "Poppins-Bold.ttf")
FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "Poppins-Regular.ttf")

SYSTEM_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SYSTEM_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def get_font(size, style="regular"):
    path = FONT_BOLD if style == "bold" else FONT_REGULAR
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


def create_tool_card(tool_name, short_description, price_type, emoji, score,
                     watermark="@Ai_Drop_Daily"):
    W, H = 1920, 1080

    # ── Background ──────────────────────────────────────────────
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

    # ── Card ────────────────────────────────────────────────────
    card_w, card_h = 1140, 580
    card_x = (W - card_w) // 2
    card_y = (H - card_h) // 2 - 20   # slightly above center (visual balance)

    # Shadow layers
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

    # ── Fonts ───────────────────────────────────────────────────
    title_font = get_font(108, "bold")
    desc_font  = get_font(46,  "regular")

    # ── Description line-wrapping ───────────────────────────────
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

    # ── Measure real heights ────────────────────────────────────
    t_bbox  = fd.textbbox((0, 0), tool_name, font=title_font)
    title_w = t_bbox[2] - t_bbox[0]
    title_h = t_bbox[3] - t_bbox[1]

    line_gap  = 68                        # px between desc lines
    desc_h    = title_h + (len(lines) - 1) * line_gap if lines else 0
    # single desc line height
    if lines:
        d_bbox   = fd.textbbox((0, 0), lines[0], font=desc_font)
        one_line = d_bbox[3] - d_bbox[1]
        desc_h   = one_line + max(0, len(lines) - 1) * line_gap

    GAP = 120   # space between title bottom and first desc line

    # Total block height
    total_h = title_h + GAP + desc_h

    # Centre the whole block inside card
    card_cy     = card_y + card_h // 2
    block_top   = card_cy - total_h // 2

    title_y = block_top
    desc_y  = title_y + title_h + GAP

    # ── Draw title ──────────────────────────────────────────────
    fd.text((cx - title_w // 2, title_y), tool_name,
            fill=(26, 26, 26), font=title_font)

    # ── Draw description ────────────────────────────────────────
    for i, ln in enumerate(lines):
        lw = fd.textbbox((0, 0), ln, font=desc_font)[2]
        fd.text((cx - lw // 2, desc_y + i * line_gap), ln,
                fill=(105, 107, 115), font=desc_font)

    # ── Watermark ───────────────────────────────────────────────
    wm_font = get_font(36, "regular")
    wm_bbox = fd.textbbox((0, 0), watermark, font=wm_font)
    wm_w    = wm_bbox[2] - wm_bbox[0]
    fd.text((cx - wm_w // 2, H - 80), watermark,
            fill=(160, 162, 170), font=wm_font)

    # ── Save ────────────────────────────────────────────────────
    img = img.convert("RGB")
    out = "temp_card.png"
    img.save(out, "PNG", quality=100)
    logger.info(f"Banner created: {out}")
    return out
