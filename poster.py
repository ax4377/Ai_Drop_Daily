"""
poster.py
Google Sheets se aaye formatted captions ko Telegram channel pe post karta hai.
Ab sirf caption text post hoga — image ya Gemini analysis nahi.
"""
import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def post_tools_to_channel(tools_list):
    """
    tools_list: list of dicts with 'caption' key (fetcher.py se aata hai)
    Har tool ka caption seedha Telegram channel pe post karta hai.
    """
    from config import TELEGRAM_BOT_TOKEN
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    for tool in tools_list:
        try:
            caption = tool.get("caption", "").strip()
            if not caption:
                logger.warning("Empty caption — skipping tool")
                continue

            await bot.send_message(
                chat_id="@Ai_Drop_Daily",
                text=caption,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            logger.info(f"Posted tool to channel: {caption[:60]}...")
            await asyncio.sleep(30)  # Tools ke beech delay

        except TelegramError as e:
            logger.error(f"Telegram error posting tool: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error posting tool: {e}")
            continue


async def post_morning_digest(tools_list):
    from settings import FIRST_MAX_TOOLS
    try:
        await post_tools_to_channel(tools_list[:FIRST_MAX_TOOLS])
    except Exception as e:
        logger.error(f"Error in morning digest: {e}")


async def post_evening_pick(tools_list):
    from settings import SECOND_MAX_TOOLS
    try:
        await post_tools_to_channel(tools_list[:SECOND_MAX_TOOLS])
    except Exception as e:
        logger.error(f"Error in evening pick: {e}")
