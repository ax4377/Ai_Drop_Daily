from PIL import Image, ImageDraw, ImageFont
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tool_card(tool_name, short_description, price_type, emoji, score):
    """
    Create a 1080x1080 pixel image card for the AI tool.
    Returns the file path of the generated image.
    Features:
    - Dark background
    - Cyan top border
    - Tool emoji and name
    - Short description
    - Price badge (green/red)
    - Score display
    - Watermark
    """
    try:
        # Create a dark background image
        width, height = 1080, 1080
        image = Image.new('RGB', (width, height), color='#0D1117')
        draw = ImageDraw.Draw(image)

        # Add gradient-like effect using multiple rectangles
        for i in range(0, height, 20):
            intensity = 13 + (i // 20) % 3
            color = f'#{intensity:02x}1117'
            draw.rectangle([(0, i), (width, i + 20)], fill=color)

        # Add cyan top border (8px)
        draw.rectangle([(0, 0), (width, 8)], fill='#00D4FF')

        # Try to load fonts, fallback to default if not available
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 60)
            font_medium = ImageFont.truetype("arial.ttf", 36)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            logger.warning("Custom font not found, using default font")
            font_bold = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Write "AI Drop Daily" watermark at bottom center
        watermark_text = "AI Drop Daily"
        try:
            watermark_width = draw.textbbox((0, 0), watermark_text, font=font_small)[2]
            watermark_height = draw.textbbox((0, 0), watermark_text, font=font_small)[3]
        except Exception:
            watermark_width, watermark_height = 100, 20
        watermark_x = (width - watermark_width) // 2
        watermark_y = height - watermark_height - 20
        draw.text((watermark_x, watermark_y), watermark_text, fill='#666666', font=font_small)

        # Draw emoji at top center
        title_y = 80
        emoji_size = 80
        emoji_x = (width - emoji_size) // 2
        draw.text((emoji_x, title_y), emoji, fill='#FFFFFF', font=font_bold)

        # Draw tool name below emoji
        tool_name_y = title_y + emoji_size + 10
        try:
            tool_name_width = draw.textbbox((0, 0), tool_name, font=font_bold)[2]
            tool_name_height = draw.textbbox((0, 0), tool_name, font=font_bold)[3]
        except Exception:
            tool_name_width, tool_name_height = 400, 60
        tool_name_x = (width - tool_name_width) // 2
        draw.text((tool_name_x, tool_name_y), tool_name, fill='#FFFFFF', font=font_bold)

        # Write short description below tool name with word wrap
        desc_y = tool_name_y + tool_name_height + 20
        max_chars_per_line = 30
        words = short_description.split()
        lines = []
        current_line = []
        current_length = 0
        for word in words:
            if current_length + len(word) + len(current_line) <= max_chars_per_line:
                current_line.append(word)
                current_length += len(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        if current_line:
            lines.append(' '.join(current_line))

        # Limit to 2 lines
        lines = lines[:2]
        for i, line in enumerate(lines):
            line_y = desc_y + i * 40
            try:
                line_width = draw.textbbox((0, 0), line, font=font_medium)[2]
            except Exception:
                line_width = 300
            line_x = (width - line_width) // 2
            draw.text((line_x, line_y), line, fill='#CCCCCC', font=font_medium)

        # Add price badge
        badge_y = desc_y + 100
        badge_padding = 10

        # Badge color based on price type
        if price_type == "Free":
            badge_color = '#00FF88'
        elif price_type == "Freemium":
            badge_color = '#FFD700'
        else:
            badge_color = '#FF4444'

        # Draw badge
        try:
            badge_text_width = draw.textbbox((0, 0), price_type, font=font_small)[2]
            badge_text_height = draw.textbbox((0, 0), price_type, font=font_small)[3]
        except Exception:
            badge_text_width, badge_text_height = 60, 24

        badge_width = badge_text_width + 2 * badge_padding
        badge_height = badge_text_height + 2 * badge_padding
        badge_x = width - badge_width - 20

        draw.rectangle(
            [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
            fill=badge_color
        )
        draw.text((badge_x + badge_padding, badge_y + badge_padding), price_type, fill='#000000', font=font_small)

        # Add score at bottom left
        score_text = f"Score: {score}/10"
        try:
            score_height = draw.textbbox((0, 0), score_text, font=font_medium)[3]
        except Exception:
            score_height = 36
        score_x = 20
        score_y = height - score_height - 20
        draw.text((score_x, score_y), score_text, fill='#00D4FF', font=font_medium)

        # Save image
        temp_file_path = "temp_card.png"
        image.save(temp_file_path)
        logger.info(f"Image card created: {temp_file_path}")
        return temp_file_path

    except Exception as e:
        logger.error(f"Error creating image card: {e}")
        try:
            # Fallback - simple black image
            image = Image.new('RGB', (1080, 1080), color='#0D1117')
            draw = ImageDraw.Draw(image)
            draw.text((100, 500), "AI Drop Daily", fill='#FFFFFF')
            temp_file_path = "temp_card.png"
            image.save(temp_file_path)
            return temp_file_path
        except Exception as e2:
            logger.error(f"Fallback image also failed: {e2}")
            return ""
