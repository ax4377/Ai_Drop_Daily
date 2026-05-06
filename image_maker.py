"""
image_maker.py
Generates a premium 16:9 banner using PIL only.
Design: Warm beige background + gold gradient title + glassmorphism card.
Fonts are bundled in ./fonts/ folder — works on Railway too.
"""
import logging
import os
import numpy as np
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


def make_gold_gradient_text(img, text, font, cx, y, W):
    """Render text with a smooth gold gradient."""
    dummy_draw = ImageDraw.Draw(img)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2

    # Create text mask
    mask = Image.new("L", (tw + 20, th + 20), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((-bbox[0] + 10, -bbox[1] + 10), text, fill=255, font=font)

    # Gold gradient array
    grad_arr = np.zeros((th + 20, tw + 20, 4), dtype=np.uint8)
    for x in range(tw + 20):
        t = x / max(tw + 19, 1)
        if t < 0.4:
            s = t / 0.4
            r = int(139 + s * (212 - 139))
            g = int(90  + s * (160 - 90))
            b = int(20  + s * (40  - 20))
        elif t < 0.7:
            s = (t - 0.4) / 0.3
            r = int(212 + s * (230 - 212))
            g = int(160 + s * (185 - 160))
            b = int(40  + s * (70  - 40))
        else:
            s = (t - 0.7) / 0.3
            r = int(230 - s * (230 - 180))
            g = int(185 - s * (185 - 130))
            b = int(70  - s * (70  - 30))
        grad_arr[:, x] = [r, g, b, 255]

    grad = Image.fromarray(grad_arr, "RGBA")
    grad.putalpha(mask)
    img.paste(grad, (tx - 10, y - 10), grad)
    return tw, th


def create_tool_card(tool_name, short_description, price_type, emoji, score,
                     watermark="@AiTool_s"):
    W, H = 1920, 1080

    # ── Background: warm beige diagonal gradient ─────────────────
    bg_arr = np.zeros((H, W, 4), dtype=np.uint8)
    for y in range(H):
        t_row = y / H
        for x in range(W):
            t = x / W * 0.5 + t_row * 0.5
            r = int(245 - t * 12)
            g = int(240 - t * 14)
            b = int(228 - t * 18)
            bg_arr[y, x] = [r, g, b, 255]
    img = Image.fromarray(bg_arr, "RGBA")

    # ── Subtle warm grid ─────────────────────────────────────────
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    grid_color = (180, 165, 145, 40)
    for x in range(0, W, 55):
        gd.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, 55):
        gd.line([(0, y), (W, y)], fill=grid_color, width=1)
    img = Image.alpha_composite(img, grid)

    # ── Soft warm center glow ─────────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W//2 - 600, H//2 - 200, W//2 + 600, H + 300],
                                  fill=(235, 210, 160, 35))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.alpha_composite(img, glow)

    # ── Card ─────────────────────────────────────────────────────
    card_w, card_h = 1200, 580
    card_x = (W - card_w) // 2
    card_y = (H - card_h) // 2 - 20

    # Warm shadow layers
    for s_off, s_blur, s_alpha in [(60, 100, 18), (25, 45, 12), (10, 20, 8)]:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_rounded_rect(ImageDraw.Draw(sh),
            [card_x + 15, card_y + s_off, card_x + card_w - 15, card_y + card_h + s_off],
            48, fill=(160, 140, 110, s_alpha))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(s_blur)))

    # Card body: warm creamy white
    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(card_layer),
        [card_x, card_y, card_x + card_w, card_y + card_h],
        48, fill=(250, 247, 240, 242))
    img = Image.alpha_composite(img, card_layer)

    # Top edge shine
    shine = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_rounded_rect(ImageDraw.Draw(shine),
        [card_x + 2, card_y + 2, card_x + card_w - 2, card_y + 60],
        48, fill=(255, 255, 255, 60))
    img = Image.alpha_composite(img, shine)

    # ── Fonts ────────────────────────────────────────────────────
    title_font = get_font(108, "bold")
    desc_font  = get_font(46,  "regular")

    fd = ImageDraw.Draw(img)
    cx = W // 2

    # ── Description line-wrapping ─────────────────────────────────
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

    # ── Measure heights ───────────────────────────────────────────
    t_bbox  = fd.textbbox((0, 0), tool_name, font=title_font)
    title_w = t_bbox[2] - t_bbox[0]
    title_h = t_bbox[3] - t_bbox[1]

    line_gap = 68
    if lines:
        d_bbox   = fd.textbbox((0, 0), lines[0], font=desc_font)
        one_line = d_bbox[3] - d_bbox[1]
        desc_h   = one_line + max(0, len(lines) - 1) * line_gap
    else:
        desc_h = 0

    GAP       = 110
    total_h   = title_h + GAP + desc_h
    card_cy   = card_y + card_h // 2
    block_top = card_cy - total_h // 2

    title_y = block_top
    desc_y  = title_y + title_h + GAP

    # ── Draw title with gold gradient ────────────────────────────
    make_gold_gradient_text(img, tool_name, title_font, cx, title_y, W)

    # ── Draw description (warm brown-grey) ───────────────────────
    fd = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        lw = fd.textbbox((0, 0), ln, font=desc_font)[2]
        fd.text((cx - lw // 2, desc_y + i * line_gap), ln,
                fill=(140, 115, 85, 220), font=desc_font)

    # ── Watermark ────────────────────────────────────────────────
    wm_font = get_font(36, "regular")
    wm_bbox = fd.textbbox((0, 0), watermark, font=wm_font)
    wm_w    = wm_bbox[2] - wm_bbox[0]
    fd.text((cx - wm_w // 2, H - 80), watermark,
            fill=(180, 155, 120, 180), font=wm_font)

    # ── Save ─────────────────────────────────────────────────────
    img = img.convert("RGB")
    out = "temp_card.png"
    img.save(out, "PNG", quality=100)
    logger.info(f"Banner created: {out}")
    return out
