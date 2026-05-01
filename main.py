import asyncio
import logging
from database import init_db
from telegram.ext import Application, CommandHandler
from bot_commands import cmd_start, cmd_status, cmd_setpost, cmd_testnow, cmd_help
from config import TELEGRAM_BOT_TOKEN
from scheduler import setup_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the AI Drop Daily Bot."""
    try:
        # Step 1: Initialize database
        init_db()
        
        # Step 2: Build Telegram Application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Step 3: Add all command handlers
        application.add_handler(CommandHandler("start", cmd_start))
        application.add_handler(CommandHandler("status", cmd_status))
        application.add_handler(CommandHandler("setpost", cmd_setpost))
        application.add_handler(CommandHandler("testnow", cmd_testnow))
        application.add_handler(CommandHandler("help", cmd_help))
        
        # Step 4: Setup scheduler but pass application.job_queue to it
        setup_scheduler(application)
        
        # Step 5: Start the application with polling
        async with application:
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            logging.info("AI Drop Daily Bot Started Successfully")
            logging.info("Bot is now running and listening for commands...")
            await asyncio.sleep(float("inf"))
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error in bot loop: {e}")

if __name__ == "__main__":
    asyncio.run(main())
