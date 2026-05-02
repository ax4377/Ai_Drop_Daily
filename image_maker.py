from PIL import Image, ImageDraw, ImageFont, ImageFilter
import logging
import os
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_font(size, bold=False):
    bold_fonts = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "arialbd.ttf",
    ]
    regular_fonts = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "arial.ttf",
    ]
    font_list = bold_fonts if bold else regular_fonts
    for path in font_list:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    try:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline, width=width)


def create_tool_card(tool_name, short_description, price_type, emoji, score):
    """
    Premium 16:9 (1920x1080) minimal banner — Apple/Notion style.
    Only two elements: Title (emoji + name) and Description.
    No price badge, no score, no extra elements.
    """
    try:
        W, H = 1920, 1080
        image = Image.new('RGBA', (W, H), (247, 248, 250, 255))

        # 1. Subtle grid (5% opacity)
        draw = ImageDraw.Draw(image)
        grid_spacing = 72
        for x in range(0, W, grid_spacing):
            draw.line([(x, 0), (x, H)], fill=(0, 0, 0, 13), width=1)
        for y in range(0, H, grid_spacing):
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, 13), width=1)

        # 2. Smooth top-left lighting blob
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([-350, -350, 950, 750], fill=(195, 210, 255, 18))
        glow = glow.filter(ImageFilter.GaussianBlur(130))
        image = Image.alpha_composite(image, glow)

        # 3. Light grain texture (2%)
        grain = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gn = ImageDraw.Draw(grain)
        for _ in range(19200):
            gn.point(
                (random.randint(0, W - 1), random.randint(0, H - 1)),
                fill=(0, 0, 0, random.randint(8, 18))
            )
        image = Image.alpha_composite(image, grain)

        # 4. Glassmorphism card
        card_w, card_h = 1120, 540
        card_x = (W - card_w) // 2
        card_y = (H - card_h) // 2
        radius = 28

        for s_off, s_blur, s_alpha in [(38, 55, 14), (12, 22, 9)]:
            shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            draw_rounded_rectangle(
                sd,
                [card_x, card_y + s_off, card_x + card_w, card_y + card_h + s_off],
                radius=radius, fill=(0, 0, 0, s_alpha)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(s_blur))
            image = Image.alpha_composite(image, shadow)

        card_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        cl = ImageDraw.Draw(card_layer)
        draw_rounded_rectangle(
            cl, [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius, fill=(255, 255, 255, 230)
        )
        draw_rounded_rectangle(
            cl, [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius, outline=(0, 0, 0, 13), width=1
        )
        image = Image.alpha_composite(image, card_layer)

        # Top highlight (glass reflection)
        hl_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        hl = ImageDraw.Draw(hl_layer)
        draw_rounded_rectangle(
            hl, [card_x + 2, card_y + 2, card_x + card_w - 2, card_y + 10],
            radius=radius, fill=(255, 255, 255, 150)
        )
        image = Image.alpha_composite(image, hl_layer)

        # 5. Content — only TWO elements
        fd = ImageDraw.Draw(image)
        cx = W // 2
        card_cy = card_y + card_h // 2

        # ─ Element 1: Title (emoji + name), BIG BOLD ─
        font_title = get_font(86, bold=True)
        title_text = f"{emoji}  {tool_name}"
        try:
            tb = fd.textbbox((0, 0), title_text, font=font_title)
            tw = tb[2] - tb[0]
        except Exception:
            tw = 600
        title_y = card_cy - 90

        # Subtle glow on title
        glow_t = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gt = ImageDraw.Draw(glow_t)
        gt.text((cx - tw // 2, title_y), title_text, fill=(90, 110, 255, 36), font=font_title)
        glow_t = glow_t.filter(ImageFilter.GaussianBlur(14))
        image = Image.alpha_composite(image, glow_t)

        fd = ImageDraw.Draw(image)
        fd.text((cx - tw // 2, title_y), title_text, fill=(17, 17, 17), font=font_title)

        # ─ Element 2: Description (below title, clean spacing) ─
        font_desc = get_font(42, bold=False)
        desc_color = (85, 85, 85)
        desc_y = title_y + 120

        max_width = card_w - 180
        words = short_description.split()
        lines, line = [], []
        for word in words:
            test = ' '.join(line + [word])
            try:
                lw = fd.textbbox((0, 0), test, font=font_desc)[2]
            except Exception:
                lw = len(test) * 23
            if lw <= max_width:
                line.append(word)
            else:
                if line:
                    lines.append(' '.join(line))
                line = [word]
        if line:
            lines.append(' '.join(line))
        lines = lines[:2]

        for i, ln in enumerate(lines):
            try:
                lw = fd.textbbox((0, 0), ln, font=font_desc)[2]
            except Exception:
                lw = 300
            fd.text((cx - lw // 2, desc_y + i * 58), ln, fill=desc_color, font=font_desc)

        # 6. Watermark
        font_wm = get_font(28, bold=False)
        wm_text = "AI Drop Daily"
        try:
            wmw = fd.textbbox((0, 0), wm_text, font=font_wm)[2]
        except Exception:
            wmw = 150
        fd.text((cx - wmw // 2, H - 46), wm_text, fill=(190, 190, 190), font=font_wm)

        # 7. Save
        image = image.convert('RGB')
        out_path = "temp_card.png"
        image.save(out_path, "PNG", quality=100)
        logger.info(f"16:9 premium banner saved: {out_path}")
        return out_path

    except Exception as e:
        logger.error(f"Error creating image: {e}")
        try:
            image = Image.new('RGB', (1920, 1080), '#F7F8FA')
            ImageDraw.Draw(image).text((100, 500), "AI Drop Daily", fill='#111111')
            out_path = "temp_card.png"
            image.save(out_path)
            return out_path
        except Exception as e2:
            logger.error(f"Fallback failed: {e2}")
            return ""
