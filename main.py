"""
main.py
Entry point for AI Drop Daily Bot.

Fixes applied:
- 409 Conflict fix: proper wait + retry after delete_webhook
- FileHandler removed (Railway pe stdout hi persist hota hai)
- New commands registered: /listtoday, /cleardb
- Graceful shutdown on KeyboardInterrupt
"""

import asyncio
import logging
from database import init_db
from telegram import Bot
from telegram.ext import Application, CommandHandler
from telegram.error import Conflict, NetworkError, TimedOut
from bot_commands import (
    cmd_start, cmd_status, cmd_setpost,
    cmd_testnow, cmd_help, cmd_listtoday, cmd_cleardb,
)
from config import TELEGRAM_BOT_TOKEN
from scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def clear_webhook_with_retry(bot: Bot, max_attempts: int = 5) -> bool:
    """
    Webhook delete karo + 409 Conflict clear hone tak wait karo.
    Railway redeploy pe purani instance kuch seconds tak alive rehti hai.
    Progressive backoff: 3s, 6s, 9s, 12s...
    """
    for attempt in range(1, max_attempts + 1):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info(f"Webhook cleared (attempt {attempt})")
            await asyncio.sleep(3)   # Telegram servers ko settle hone do
            return True
        except Conflict as e:
            logger.warning(f"Conflict on attempt {attempt}: {e}")
            if attempt < max_attempts:
                wait = attempt * 3
                logger.info(f"Waiting {wait}s before retry...")
                await asyncio.sleep(wait)
        except (NetworkError, TimedOut) as e:
            logger.warning(f"Network error on attempt {attempt}: {e}")
            if attempt < max_attempts:
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error clearing webhook: {e}")
            break

    logger.error("Could not clear webhook after all attempts. Proceeding anyway.")
    return False


async def main():
    """Main entry point."""
    try:
        # 1. Database init
        init_db()
        logger.info("Database initialized.")

        # 2. Build application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # 3. Clear webhook + wait for 409 window to pass
        await clear_webhook_with_retry(application.bot)

        # 4. Register ALL command handlers
        application.add_handler(CommandHandler("start",     cmd_start))
        application.add_handler(CommandHandler("status",    cmd_status))
        application.add_handler(CommandHandler("setpost",   cmd_setpost))
        application.add_handler(CommandHandler("testnow",   cmd_testnow))
        application.add_handler(CommandHandler("listtoday", cmd_listtoday))
        application.add_handler(CommandHandler("cleardb",   cmd_cleardb))
        application.add_handler(CommandHandler("help",      cmd_help))
        logger.info("Command handlers registered.")

        # 5. Setup scheduler
        setup_scheduler(application)

        # 6. Start polling
        async with application:
            await application.start()
            await application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message"],
            )
            logger.info("AI Drop Daily Bot started. Listening...")
            await asyncio.sleep(float("inf"))

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
