"""
image_maker.py
Generates a premium 16:9 banner using PIL only.

Fixes applied:
- Score badge added (bottom-left corner of card)
- Price tag badge added (bottom-right corner of card)
- Emoji shown next to tool name
- Fonts bundled in ./fonts/ — works on Railway too
"""

import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD    = os.path.join(BASE_DIR, "fonts", "Poppins-Bold.ttf")
FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "Poppins-Regular.ttf")

SYSTEM_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SYSTEM_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def get_font(size: int, style: str = "regular") -> ImageFont.FreeTypeFont:
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


def _price_color(price_type: str) -> tuple:
    """Price badge ka background color."""
    mapping = {
        "Free":     (34, 197, 94),    # green
        "Freemium": (234, 179, 8),    # yellow
        "Paid":     (239, 68, 68),    # red
    }
    return mapping.get(price_type, (148, 163, 184))


def create_tool_card(
    tool_name: str,
    short_description: str,
    price_type: str,
    emoji: str,
    score: int,
    watermark: str = "@Ai_Drop_Daily",
) -> str:
    W, H = 1920, 1080

    # ── Background ──────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (235, 237, 242, 255))

    # Subtle grid
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grid)
    for x in range(0, W, 60):
        gd.line([(x, 0), (x, H)], fill=(170, 175, 195, 30), width=1)
    for y in range(0, H, 60):
        gd.line([(0, y), (W, y)], fill=(170, 175, 195, 30), width=1)
    img = Image.alpha_composite(img, grid)

    # Bottom-right soft glow
    br_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(br_glow).ellipse([W - 700, H - 550, W + 350, H + 250], fill=(215, 218, 232, 60))
    br_glow = br_glow.filter(ImageFilter.GaussianBlur(130))
    img = Image.alpha_composite(img, br_glow)

    # ── Card ────────────────────────────────────────────────────
    card_w, card_h = 1140, 600
    card_x = (W - card_w) // 2
    card_y = (H - card_h) // 2 - 20

    # Shadow layers
    for s_off, s_blur, s_alpha in [(50, 80, 16), (20, 35, 10), (8, 16, 7)]:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_rounded_rect(
            ImageDraw.Draw(sh),
            [card_x + 10, card_y + s_off, card_x + card_w - 10, card_y + card_h + s_off],
            32,
            fill=(140, 145, 165, s_alpha),
        )
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(s_blur)))

    # Card body
    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(
        ImageDraw.Draw(card_layer),
        [card_x, card_y, card_x + card_w, card_y + card_h],
        32,
        fill=(251, 252, 254, 250),
    )
    img = Image.alpha_composite(img, card_layer)

    fd = ImageDraw.Draw(img)
    cx = W // 2

    # ── Fonts ───────────────────────────────────────────────────
    title_font = get_font(96, "bold")
    desc_font  = get_font(44, "regular")
    badge_font = get_font(34, "bold")
    wm_font    = get_font(34, "regular")

    # ── Title line: emoji + tool name ───────────────────────────
    title_text = f"{emoji}  {tool_name}"
    t_bbox     = fd.textbbox((0, 0), title_text, font=title_font)
    title_w    = t_bbox[2] - t_bbox[0]
    title_h    = t_bbox[3] - t_bbox[1]

    # ── Description line-wrapping ───────────────────────────────
    max_w = card_w - 200
    words = short_description.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        lw   = fd.textbbox((0, 0), test, font=desc_font)[2]
        if lw <= max_w:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    lines = lines[:2]   # max 2 lines

    # ── Measure real heights ────────────────────────────────────
    line_gap = 64
    if lines:
        d_bbox   = fd.textbbox((0, 0), lines[0], font=desc_font)
        one_line = d_bbox[3] - d_bbox[1]
        desc_h   = one_line + max(0, len(lines) - 1) * line_gap
    else:
        desc_h = 0

    GAP = 110   # space between title bottom and first desc line

    # Badge area height (score + price badges at card bottom)
    BADGE_AREA = 80

    total_h   = title_h + GAP + desc_h
    card_cy   = card_y + (card_h - BADGE_AREA) // 2
    block_top = card_cy - total_h // 2

    title_y = block_top
    desc_y  = title_y + title_h + GAP

    # ── Draw title ──────────────────────────────────────────────
    fd.text(
        (cx - title_w // 2, title_y),
        title_text,
        fill=(26, 26, 26),
        font=title_font,
    )

    # ── Draw description ────────────────────────────────────────
    for i, ln in enumerate(lines):
        lw = fd.textbbox((0, 0), ln, font=desc_font)[2]
        fd.text(
            (cx - lw // 2, desc_y + i * line_gap),
            ln,
            fill=(105, 107, 115),
            font=desc_font,
        )

    # ── Score Badge (bottom-left of card) ───────────────────────
    badge_y     = card_y + card_h - 64
    score_text  = f"⭐ {score}/10"
    sb_bbox     = fd.textbbox((0, 0), score_text, font=badge_font)
    sb_w        = sb_bbox[2] - sb_bbox[0] + 32
    sb_h        = sb_bbox[3] - sb_bbox[1] + 18
    sb_x        = card_x + 40

    draw_rounded_rect(fd, [sb_x, badge_y, sb_x + sb_w, badge_y + sb_h], 14, fill=(241, 245, 249))
    fd.text((sb_x + 16, badge_y + 9), score_text, fill=(51, 65, 85), font=badge_font)

    # ── Price Badge (bottom-right of card) ──────────────────────
    price_text = f"💰 {price_type}"
    pb_bbox    = fd.textbbox((0, 0), price_text, font=badge_font)
    pb_w       = pb_bbox[2] - pb_bbox[0] + 32
    pb_h       = pb_bbox[3] - pb_bbox[1] + 18
    pb_x       = card_x + card_w - pb_w - 40

    price_bg = _price_color(price_type) + (40,)   # light tint
    badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(badge_layer), [pb_x, badge_y, pb_x + pb_w, badge_y + pb_h], 14, fill=price_bg)
    img = Image.alpha_composite(img, badge_layer)

    fd = ImageDraw.Draw(img)   # redraw after alpha composite
    fd.text((pb_x + 16, badge_y + 9), price_text, fill=_price_color(price_type)[:3], font=badge_font)

    # ── Watermark ───────────────────────────────────────────────
    wm_bbox = fd.textbbox((0, 0), watermark, font=wm_font)
    wm_w    = wm_bbox[2] - wm_bbox[0]
    fd.text((cx - wm_w // 2, H - 80), watermark, fill=(160, 162, 170), font=wm_font)

    # ── Save ────────────────────────────────────────────────────
    img = img.convert("RGB")
    out = "temp_card.png"
    img.save(out, "PNG", quality=100)
    logger.info(f"Banner created: {out}")
    return out
