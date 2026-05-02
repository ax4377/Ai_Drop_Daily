import asyncio
import logging
import os
from telegram import Bot
from telegram.error import TelegramError
from gemini_helper import analyze_tool
from image_maker import create_tool_card
from database import save_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_tags(price_type, category):
    if price_type == "Free":
        price_tag = "#free"
    elif price_type == "Paid":
        price_tag = "#paid"
    else:
        price_tag = "#freemium"

    category_words = category.strip().split()
    if category_words:
        category_base = category_words[0].lower()
        category_base = ''.join(c for c in category_base if c.isalnum())
        category_tag = f"#{category_base}" if category_base else "#other"
    else:
        category_tag = "#other"

    return f"{price_tag} {category_tag} #AITools @Ai_Drop_Daily"


async def post_tools_to_channel(tools_list, session_type):
    """Post tools to Telegram channel.
    Reuses _cached_analysis from scheduler (evening) to avoid double API call.
    Morning tools have no cache — analyze_tool called fresh here.
    """
    from config import TELEGRAM_BOT_TOKEN
    bot = Bot(token=TELEGRAM_BOT_TOKEN)  # Single Bot instance for all tools

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
                score=tool_info["score"]
            )

            if not image_path or not os.path.exists(image_path):
                logger.error(f"Failed to create image for {tool['name']}")
                continue

            tags = generate_tags(tool_info["price_type"], tool_info.get("category", "Other"))
            caption = f"""{tool_info['emoji']} {tool['name']}

📝 {tool_info['short_description']}

🎯 Use Case: {tool_info['use_case']}

💰 Price: {tool_info['price_type']}

⭐ Score: {tool_info['score']}/10

🔗 {tool['link']}

{tags}"""

            with open(image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id="@Ai_Drop_Daily",
                    photo=photo,
                    caption=caption
                )

            logger.info(f"Posted tool: {tool['name']} to channel")

            save_tool(
                tool_name=tool["name"],
                tool_link=tool["link"],
                tool_description=tool_info["short_description"],
                price_type=tool_info["price_type"],
                post_session=session_type,
                gemini_score=tool_info["score"]
            )

            if os.path.exists(image_path):
                os.remove(image_path)

            await asyncio.sleep(30)

        except TelegramError as e:
            logger.error(f"Telegram error posting {tool['name']}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error posting {tool['name']}: {e}")
            continue


async def post_morning_digest(tools_list):
    from settings import FIRST_MAX_TOOLS
    try:
        await post_tools_to_channel(tools_list[:FIRST_MAX_TOOLS], "morning")
    except Exception as e:
        logger.error(f"Error in morning digest: {e}")


async def post_evening_pick(tools_list):
    from settings import SECOND_MAX_TOOLS
    try:
        await post_tools_to_channel(tools_list[:SECOND_MAX_TOOLS], "evening")
    except Exception as e:
        logger.error(f"Error in evening pick: {e}")
