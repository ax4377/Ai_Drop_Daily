import asyncio
import logging
import os
from telegram import Bot
from telegram.error import TelegramError
from gemini_helper import analyze_tool
from image_maker import create_tool_card
from database import save_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_tools_to_channel(tools_list, session_type):
    """
    Post a list of tools to the Telegram channel.
    For each tool, analyze with Gemini, create an image, and post to channel.
    """
    # Get bot token from environment variable (loaded via config in other modules, but we need it here too)
    from config import TELEGRAM_BOT_TOKEN
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    for tool in tools_list:
        try:
            logger.info(f"Processing tool: {tool['name']}")
            
            # Analyze the tool with Gemini
            tool_info = analyze_tool(tool['name'], tool['summary'], tool['link'])
            
            # Create the image card
            image_path = create_tool_card(
                tool_name=tool['name'],
                short_description=tool_info['short_description'],
                price_type=tool_info['price_type'],
                emoji=tool_info['emoji'],
                score=tool_info['score']
            )
            
            if not image_path or not os.path.exists(image_path):
                logger.error(f"Failed to create image for {tool['name']}")
                continue
            
            # Prepare the caption
            caption = f"""{tool_info['emoji']} {tool['name']}

📝 {tool_info['short_description']}

🎯 Use: {tool_info['use_case']}

💰 Price: {tool_info['price_type']}

⭐ Score: {tool_info['score']}/10

🔗 {tool['link']}

#AITools #NewAI #AIDrop"""
            
            # Send the image to the channel
            with open(image_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id="@Ai_Drop_Daily",
                    photo=photo,
                    caption=caption
                )
            
            logger.info(f"Posted tool: {tool['name']} to channel")
            
            # Save to database
            save_tool(
                tool_name=tool['name'],
                tool_link=tool['link'],
                tool_description=tool_info['short_description'],
                price_type=tool_info['price_type'],
                post_session=session_type,
                gemini_score=tool_info['score']
            )
            
            # Delete the temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Wait 30 seconds before posting the next tool to avoid spam
            await asyncio.sleep(30)
            
        except TelegramError as e:
            logger.error(f"Telegram error posting {tool['name']}: {e}")
            continue  # Continue with the next tool
        except Exception as e:
            logger.error(f"Unexpected error posting {tool['name']}: {e}")
            continue  # Continue with the next tool

async def post_morning_digest(tools_list):
    """
    Post the morning digest: first send a header message, then post the tools.
    """
    from config import TELEGRAM_BOT_TOKEN
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    try:
        # Send header message
        await bot.send_message(
            chat_id="@Ai_Drop_Daily",
            text="🌅 Good Morning! Aaj ke naye AI Tools aa gaye hain 👇"
        )
        logger.info("Morning header message sent")
        
        # Post the tools (limit to morning max)
        max_tools = 5  # From config, but we can import if needed
        await post_tools_to_channel(tools_list[:max_tools], "morning")
        
    except Exception as e:
        logger.error(f"Error in morning digest: {e}")

async def post_evening_pick(tools_list):
    """
    Post the evening pick: first send a header message, then post the tools.
    """
    from config import TELEGRAM_BOT_TOKEN
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    try:
        # Send header message
        await bot.send_message(
            chat_id="@Ai_Drop_Daily",
            text="🌆 Evening Best Pick! Aaj ka sabse best AI tool 👇"
        )
        logger.info("Evening header message sent")
        
        # Post the tools (limit to evening max)
        max_tools = 2  # From config
        await post_tools_to_channel(tools_list[:max_tools], "evening")
        
    except Exception as e:
        logger.error(f"Error in evening pick: {e}")