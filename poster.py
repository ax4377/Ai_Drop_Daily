"""
poster.py
Posts AI tools to the Telegram channel.

Fixes applied:
- channel ID ab config.py se aata hai (TELEGRAM_CHANNEL_ID), hardcode nahi
- Bot instance ek baar banao, loop mein reuse karo (same as before — correct)
- _cached_analysis reuse retained (evening job double API call avoid karta hai)
"""

import asyncio
import logging
import os
from telegram import Bot
from telegram.error import TelegramError
from gemini_helper import analyze_tool
from image_maker import create_tool_card
from database import save_tool
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_tags(price_type: str, category: str) -> str:
    if price_type == "Free":
        price_tag = "#free"
    elif price_type == "Paid":
        price_tag = "#paid"
    else:
        price_tag = "#freemium"

    category_words = category.strip().split()
    if category_words:
        category_base = category_words[0].lower()
        category_base = "".join(c for c in category_base if c.isalnum())
        category_tag  = f"#{category_base}" if category_base else "#other"
    else:
        category_tag = "#other"

    return f"{price_tag} {category_tag} #AITools @Ai_Drop_Daily"


async def post_tools_to_channel(tools_list: list, session_type: str):
    """
    Post tools to Telegram channel.
    - channel ID config.py se aata hai (fix: was hardcoded before)
    - Evening tools mein _cached_analysis hota hai (scoring pehle ho chuki)
    - Morning tools fresh analyze hote hain yahan
    """
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    for tool in tools_list:
        try:
            logger.info(f"Processing tool: {tool['name']}")

            # Reuse cached analysis if available (evening job pre-analyzed)
            # Otherwise analyze fresh (morning job)
            tool_info = tool.get("_cached_analysis") or analyze_tool(
                tool["name"], tool["summary"], tool["link"]
            )

            image_path = create_tool_card(
                tool_name=tool["name"],
                short_description=tool_info["short_description"],
                price_type=tool_info["price_type"],
                emoji=tool_info["emoji"],
                score=tool_info["score"],
            )

            if not image_path or not os.path.exists(image_path):
                logger.error(f"Failed to create image for {tool['name']}")
                continue

            tags    = generate_tags(tool_info["price_type"], tool_info.get("category", "Other"))
            caption = (
                f"{tool_info['emoji']} {tool['name']}\n\n"
                f"📝 {tool_info['short_description']}\n\n"
                f"🎯 Use Case: {tool_info['use_case']}\n\n"
                f"💰 Price: {tool_info['price_type']}\n\n"
                f"⭐ Score: {tool_info['score']}/10\n\n"
                f"🔗 {tool['link']}\n\n"
                f"{tags}"
            )

            with open(image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=TELEGRAM_CHANNEL_ID,   # fix: config se aata hai
                    photo=photo,
                    caption=caption,
                )

            logger.info(f"Posted tool: {tool['name']} to channel")

            save_tool(
                tool_name=tool["name"],
                tool_link=tool["link"],
                tool_description=tool_info["short_description"],
                price_type=tool_info["price_type"],
                post_session=session_type,
                gemini_score=tool_info["score"],
            )

            # Clean up temp image
            if os.path.exists(image_path):
                os.remove(image_path)

            await asyncio.sleep(30)

        except TelegramError as e:
            logger.error(f"Telegram error posting {tool['name']}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error posting {tool['name']}: {e}")
            continue


async def post_morning_digest(tools_list: list):
    import settings
    try:
        await post_tools_to_channel(tools_list[: settings.FIRST_MAX_TOOLS], "morning")
    except Exception as e:
        logger.error(f"Error in morning digest: {e}")


async def post_evening_pick(tools_list: list):
    import settings
    try:
        await post_tools_to_channel(tools_list[: settings.SECOND_MAX_TOOLS], "evening")
    except Exception as e:
        logger.error(f"Error in evening pick: {e}")
