from PIL import Image, ImageDraw, ImageFont, ImageFilter
import logging
import os
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_font(size, bold=False):
    """Load best available font, fallback to default."""
    bold_fonts = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "arialbd.ttf",
    ]
    regular_fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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
        fallback = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(fallback, size)
    except Exception:
        return ImageFont.load_default()


def draw_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle manually for compatibility."""
    x1, y1, x2, y2 = xy
    try:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline, width=width)


def create_tool_card(tool_name, short_description, price_type, emoji, score):
    """
    Create Apple/Notion style minimal AI tool card (1080x1080).
    Returns the file path of the generated image.
    """
    try:
        # Canvas Setup (1080x1080)
        width, height = 1080, 1080
        base_color = (248, 249, 250)
        image = Image.new('RGBA', (width, height), base_color)
        draw = ImageDraw.Draw(image)

        # Subtle Grid Pattern
        grid_spacing = 60
        grid_color = (0, 0, 0, 12)
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)

        # Light Grain Texture
        grain_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        grain_draw = ImageDraw.Draw(grain_overlay)
        for _ in range(15000):
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            grain_draw.point((x, y), fill=(0, 0, 0, 15))
        image = Image.alpha_composite(image, grain_overlay)

        # Glassmorphism Card
        card_w, card_h = 900, 700
        card_x = (width - card_w) // 2
        card_y = (height - card_h) // 2
        radius = 28

        # Soft Shadow
        shadow_layers = [(20, 35, 18), (6, 14, 10)]
        for offset, blur, opacity in shadow_layers:
            shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            s_draw = ImageDraw.Draw(shadow)
            draw_rounded_rectangle(
                s_draw,
                [card_x, card_y + offset, card_x + card_w, card_y + card_h + offset],
                radius=radius,
                fill=(0, 0, 0, opacity)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
            image = Image.alpha_composite(image, shadow)

        # Main Card Body
        card_body = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(card_body)
        draw_rounded_rectangle(
            c_draw,
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            fill=(255, 255, 255, 225)
        )
        # Card border
        draw_rounded_rectangle(
            c_draw,
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            outline=(0, 0, 0, 18),
            width=1
        )
        image = Image.alpha_composite(image, card_body)

        # Content Drawing
        final_draw = ImageDraw.Draw(image)

        # Fonts
        font_emoji = get_font(72, bold=True)
        font_title = get_font(64, bold=True)
        font_desc = get_font(34, bold=False)
        font_badge = get_font(26, bold=True)
        font_score = get_font(28, bold=True)
        font_watermark = get_font(22, bold=False)

        # Center X
        center_x = width // 2

        # Emoji
        emoji_y = card_y + 80
        try:
            emoji_w = final_draw.textbbox((0, 0), emoji, font=font_emoji)[2]
        except Exception:
            emoji_w = 72
        final_draw.text((center_x - emoji_w // 2, emoji_y), emoji, fill=(17, 17, 17), font=font_emoji)

        # Tool Name
        title_y = emoji_y + 90
        try:
            title_w = final_draw.textbbox((0, 0), tool_name, font=font_title)[2]
        except Exception:
            title_w = 400
        # Subtle shadow
        final_draw.text((center_x - title_w // 2 + 2, title_y + 2), tool_name, fill=(0, 0, 0, 30), font=font_title)
        final_draw.text((center_x - title_w // 2, title_y), tool_name, fill=(17, 17, 17), font=font_title)

        # Thin divider line
        divider_y = title_y + 80
        final_draw.line(
            [(card_x + 60, divider_y), (card_x + card_w - 60, divider_y)],
            fill=(0, 0, 0, 30),
            width=1
        )

        # Description (word wrap)
        desc_y = divider_y + 30
        max_chars = 40
        words = short_description.split()
        lines = []
        current_line = []
        current_len = 0
        for word in words:
            if current_len + len(word) + len(current_line) <= max_chars:
                current_line.append(word)
                current_len += len(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_len = len(word)
        if current_line:
            lines.append(' '.join(current_line))
        lines = lines[:3]

        for i, line in enumerate(lines):
            line_y = desc_y + i * 46
            try:
                line_w = final_draw.textbbox((0, 0), line, font=font_desc)[2]
            except Exception:
                line_w = 300
            final_draw.text((center_x - line_w // 2, line_y), line, fill=(85, 85, 85), font=font_desc)

        # Price Badge (bottom left of card)
        badge_padding_x = 20
        badge_padding_y = 10
        if price_type == "Free":
            badge_bg = (0, 200, 100, 220)
            badge_text_color = (255, 255, 255)
        elif price_type == "Freemium":
            badge_bg = (255, 180, 0, 220)
            badge_text_color = (255, 255, 255)
        else:
            badge_bg = (255, 60, 60, 220)
            badge_text_color = (255, 255, 255)

        try:
            badge_w = final_draw.textbbox((0, 0), price_type, font=font_badge)[2]
            badge_h = final_draw.textbbox((0, 0), price_type, font=font_badge)[3]
        except Exception:
            badge_w, badge_h = 70, 28

        badge_rect_w = badge_w + badge_padding_x * 2
        badge_rect_h = badge_h + badge_padding_y * 2
        badge_x = card_x + 40
        badge_y = card_y + card_h - badge_rect_h - 40

        badge_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(badge_layer)
        draw_rounded_rectangle(
            b_draw,
            [badge_x, badge_y, badge_x + badge_rect_w, badge_y + badge_rect_h],
            radius=10,
            fill=badge_bg
        )
        image = Image.alpha_composite(image, badge_layer)

        final_draw = ImageDraw.Draw(image)
        final_draw.text(
            (badge_x + badge_padding_x, badge_y + badge_padding_y),
            price_type,
            fill=badge_text_color,
            font=font_badge
        )

        # Score (bottom right of card)
        score_text = f"⭐ {score}/10"
        try:
            score_w = final_draw.textbbox((0, 0), score_text, font=font_score)[2]
            score_h = final_draw.textbbox((0, 0), score_text, font=font_score)[3]
        except Exception:
            score_w, score_h = 100, 30
        score_x = card_x + card_w - score_w - 40
        score_y = card_y + card_h - score_h - 48
        final_draw.text((score_x, score_y), score_text, fill=(50, 50, 50), font=font_score)

        # Top highlight (glass effect)
        highlight = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(highlight)
        draw_rounded_rectangle(
            h_draw,
            [card_x + 1, card_y + 1, card_x + card_w - 1, card_y + 6],
            radius=radius,
            fill=(255, 255, 255, 120)
        )
        image = Image.alpha_composite(image, highlight)

        # Watermark bottom center
        final_draw = ImageDraw.Draw(image)
        watermark_text = "AI Drop Daily"
        try:
            wm_w = final_draw.textbbox((0, 0), watermark_text, font=font_watermark)[2]
        except Exception:
            wm_w = 120
        final_draw.text(
            (center_x - wm_w // 2, height - 40),
            watermark_text,
            fill=(180, 180, 180),
            font=font_watermark
        )

        # Save
        image = image.convert('RGB')
        temp_file_path = "temp_card.png"
        image.save(temp_file_path, "PNG", quality=100)
        logger.info(f"Premium card created: {temp_file_path}")
        return temp_file_path

    except Exception as e:
        logger.error(f"Error creating image card: {e}")
        try:
            image = Image.new('RGB', (1080, 1080), color='#F8F9FA')
            draw = ImageDraw.Draw(image)
            draw.text((100, 500), "AI Drop Daily", fill='#111111')
            temp_file_path = "temp_card.png"
            image.save(temp_file_path)
            return temp_file_path
        except Exception as e2:
            logger.error(f"Fallback image also failed: {e2}")
            return ""
