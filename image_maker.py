from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import logging
import os
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_font(font_name, size, weight="Bold"):
    """Satoshi, Inter ya Poppins load karne ki koshish karega, warna default."""
    # Paths for common clean sans-serif fonts
    paths = [
        f"C:/Windows/Fonts/{font_name}.ttf",
        f"/System/Library/Fonts/Supplemental/{font_name}.ttf",
        f"/usr/share/fonts/truetype/{font_name}.ttf",
        "./fonts/Inter-Bold.ttf" # Local path check
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    
    # Fallback to standard Arial/Helvetica
    fallback = "arialbd.ttf" if weight == "Bold" else "arial.ttf"
    try:
        return ImageFont.truetype(fallback, size)
    except:
        return ImageFont.load_default()

def create_tool_card(tool_name, short_description, emoji="🤖"):
    """
    Ultra Minimal Apple/Notion Style Card (16:9)
    """
    try:
        # 1. Canvas Setup (16:9 - 1920x1080)
        width, height = 1920, 1080
        # Background: Very light grey/white
        base_color = (248, 249, 250) 
        image = Image.new('RGBA', (width, height), base_color)
        draw = ImageDraw.Draw(image)

        # 2. Add Subtle Grid Pattern (5% Opacity)
        grid_spacing = 60
        grid_color = (0, 0, 0, 12) # Very faint black
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)

        # 3. Add Light Grain Texture
        grain_overlay = Image.new('RGBA', (width, height), (0,0,0,0))
        grain_draw = ImageDraw.Draw(grain_overlay)
        for _ in range(20000): # Random noise
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            grain_draw.point((x, y), fill=(0, 0, 0, 15))
        image = Image.alpha_composite(image, grain_overlay)

        # 4. Draw Glassmorphism Card
        card_w, card_h = 1000, 450
        card_x = (width - card_w) // 2
        card_y = (height - card_h) // 2
        radius = 24

        # Layered Soft Shadows
        shadow_layers = [
            (20, 40, 20), # (offset, blur, opacity)
            (5, 15, 12)
        ]
        for offset, blur, opacity in shadow_layers:
            shadow = Image.new('RGBA', (width, height), (0,0,0,0))
            s_draw = ImageDraw.Draw(shadow)
            s_draw.rounded_rectangle(
                [card_x, card_y + offset, card_x + card_w, card_y + card_h + offset], 
                radius=radius, fill=(0, 0, 0, opacity)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
            image = Image.alpha_composite(image, shadow)

        # Main Card Body (White with Transparency)
        card_body = Image.new('RGBA', (width, height), (0,0,0,0))
        c_draw = ImageDraw.Draw(card_body)
        c_draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h], 
            radius=radius, fill=(255, 255, 255, 220) # Glass effect
        )
        
        # Subtle 1px Border
        c_draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h], 
            radius=radius, outline=(0, 0, 0, 15), width=1
        )
        image = Image.alpha_composite(image, card_body)

        # 5. Content Rendering
        final_draw = ImageDraw.Draw(image)
        
        # Fonts
        font_title = get_font("Inter-Bold", 100, "Bold")
        font_desc = get_font("Inter-Medium", 42, "Medium")

        # Title (Emoji + Tool Name)
        title_text = f"{emoji} {tool_name}"
        title_y = card_y + 140
        
        # Subtle Title Glow/Drop Shadow
        final_draw.text((width//2 + 2, title_y + 2), title_text, fill=(0,0,0,20), font=font_title, anchor="mm")
        # Main Title
        final_draw.text((width//2, title_y), title_text, fill=(17, 17, 17), font=font_title, anchor="mm")

        # Description
        desc_y = title_y + 110
        final_draw.text((width//2, desc_y), short_description, fill=(85, 85, 85), font=font_desc, anchor="mm")

        # 6. Lighting Effect (Top-left Reflection)
        highlight = Image.new('RGBA', (width, height), (0,0,0,0))
        h_draw = ImageDraw.Draw(highlight)
        h_draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + 5], 
            radius=radius, fill=(255, 255, 255, 100)
        )
        image = Image.alpha_composite(image, highlight)

        # Final Save
        image = image.convert('RGB') # Remove Alpha for saving
        output_path = "minimal_ai_card.png"
        image.save(output_path, "PNG", quality=100, optimize=True)
        
        logger.info(f"Premium card created: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create image: {e}")
        return ""

# Example Usage
if __name__ == "__main__":
    create_tool_card(
        tool_name="GPT-5",
        short_description="Powerful AI for writing, coding & creativity",
        emoji="🤖"
    )
