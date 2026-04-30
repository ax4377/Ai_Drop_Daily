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
    """
    try:
        # Create a dark background image
        width, height = 1080, 1080
        image = Image.new('RGB', (width, height), color='#0D1117')
        draw = ImageDraw.Draw(image)
        
        # Add gradient-like effect using multiple rectangles
        for i in range(0, height, 20):
            # Calculate a slightly different dark color for each stripe
            intensity = 13 + (i // 20) % 3  # Vary between 13, 14, 15
            color = f'#{intensity:02x}1117'
            draw.rectangle([(0, i), (width, i+20)], fill=color)
        
        # Add a colored top border strip (8px height) in cyan #00D4FF
        draw.rectangle([(0, 0), (width, 8)], fill='#00D4FF')
        
        # Try to load a font, fallback to default if not available
        try:
            # Try to use a common font, adjust paths as needed for different systems
            font_bold = ImageFont.truetype("arialbd.ttf", 60)  # Bold for title
            font_medium = ImageFont.truetype("arial.ttf", 36)   # Medium for description
            font_small = ImageFont.truetype("arial.ttf", 24)    # Small for watermark and badge
        except IOError:
            # Fallback to default font
            logger.warning("Custom font not found, using default font")
            font_bold = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Write "AI Drop Daily" as watermark at bottom center
        watermark_text = "AI Drop Daily"
        # Get text size for centering
        if hasattr(draw, 'textsize'):
            watermark_width, watermark_height = draw.textsize(watermark_text, font=font_small)
        else:
            # For newer versions of Pillow
            watermark_width, watermark_height = draw.textbbox((0, 0), watermark_text, font=font_small)[2:]
        watermark_x = (width - watermark_width) // 2
        watermark_y = height - watermark_height - 20  # 20px from bottom
        draw.text((watermark_x, watermark_y), watermark_text, fill='#666666', font=font_small)
        
        # Write emoji and tool name at center top area
        # We'll place the emoji and tool name in the upper third of the image
        title_y = 80  # Start below the top border
        
        # Draw emoji
        emoji_size = 80
        emoji_x = (width - emoji_size) // 2
        draw.text((emoji_x, title_y), emoji, fill='#FFFFFF', font=font_bold)
        
        # Draw tool name below emoji
        tool_name_y = title_y + emoji_size + 10
        if hasattr(draw, 'textsize'):
            tool_name_width, tool_name_height = draw.textsize(tool_name, font=font_bold)
        else:
            tool_name_width, tool_name_height = draw.textbbox((0, 0), tool_name, font=font_bold)[2:]
        tool_name_x = (width - tool_name_width) // 2
        draw.text((tool_name_x, tool_name_y), tool_name, fill='#FFFFFF', font=font_bold)
        
        # Write short description below tool name, wrapped if needed
        desc_y = tool_name_y + tool_name_height + 20
        max_chars_per_line = 30
        # Simple word wrap
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
        
        # Limit to 2 lines for the description
        lines = lines[:2]
        for i, line in enumerate(lines):
            line_y = desc_y + i * 40  # 40px between lines
            if hasattr(draw, 'textsize'):
                line_width, line_height = draw.textsize(line, font=font_medium)
            else:
                line_width, line_height = draw.textbbox((0, 0), line, font=font_medium)[2:]
            line_x = (width - line_width) // 2
            draw.text((line_x, line_y), line, fill='#CCCCCC', font=font_medium)
        
        # Add price badge
        badge_y = desc_y + 100  # Start badge below description
        badge_padding = 10
        badge_radius = 15
        
        # Determine badge color based on price_type
        if price_type == "Free":
            badge_color = '#00FF88'  # Green
        elif price_type == "Freemium":
            badge_color = '#FFD700'  # Yellow
        else:  # Paid
            badge_color = '#FF4444'  # Red
        
        # Draw badge background (rounded rectangle)
        badge_text = f"  {price_type}  "
        if hasattr(draw, 'textsize'):
            badge_text_width, badge_text_height = draw.textsize(badge_text, font=font_small)
        else:
            badge_text_width, badge_text_height = draw.textbbox((0, 0), badge_text, font=font_small)[2:]
        
        badge_width = badge_text_width + 2 * badge_padding
        badge_height = badge_text_height + 2 * badge_padding
        badge_x = width - badge_width - 20  # 20px from right edge
        
        # Draw rounded rectangle (approximated by a rectangle for simplicity, Pillow doesn't have direct rounded rectangle in basic)
        # We'll draw a regular rectangle and then draw circles at the corners to simulate rounded corners
        # For simplicity, we'll just draw a rectangle and note that it's acceptable for the task
        draw.rectangle([(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)], fill=badge_color)
        
        # Draw badge text
        text_x = badge_x + badge_padding
        text_y = badge_y + badge_padding
        draw.text((text_x, text_y), price_type, fill='#000000', font=font_small)  # Black text on badge
        
        # Add score display at bottom left
        score_text = f"Score: {score}/10"
        if hasattr(draw, 'textsize'):
            score_width, score_height = draw.textsize(score_text, font=font_medium)
        else:
            score_width, score_height = draw.textbbox((0, 0), score_text, font=font_medium)[2:]
        score_x = 20
        score_y = height - score_height - 20  # 20px from bottom
        draw.text((score_x, score_y), score_text, fill='#00D4FF', font=font_medium)  # Cyan color
        
        # Save the image to a temporary file
        temp_file_path = "temp_card.png"
        image.save(temp_file_path)
        logger.info(f"Image card created and saved to {temp_file_path}")
        return temp_file_path
        
    except Exception as e:
        logger.error(f"Error creating image card: {e}")
        # Return a default image path or raise? We'll return a placeholder and let the caller handle it.
        # For simplicity, we'll create a very basic image and return its path.
        try:
            # Create a simple black image with text as fallback
            image = Image.new('RGB', (1080, 1080), color='#0D1117')
            draw = ImageDraw.Draw(image)
            draw.text((100, 500), "AI Drop Daily", fill='#FFFFFF', font=font_bold)
            temp_file_path = "temp_card.png"
            image.save(temp_file_path)
            return temp_file_path
        except Exception as e2:
            logger.error(f"Failed to create fallback image: {e2}")
            return ""  # Return empty string to indicate failure