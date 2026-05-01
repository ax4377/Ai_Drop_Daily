import asyncio
import logging
from scheduler import setup_scheduler
from database import init_db
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from bot_commands import (
    start_command, status_command, settime_command, testnow_command, help_command
)

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
    logger.info("AI Drop Daily Bot Started Successfully")
    
    # Initialize database
    init_db()
    
    # Set up and start scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    
    logger.info("Scheduler started. Bot is now running and waiting for scheduled jobs...")
    
    # Set up Telegram bot application for commands
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("settime", settime_command))
    application.add_handler(CommandHandler("testnow", testnow_command))
    application.add_handler(CommandHandler("help", help_command))
    
    logger.info("Telegram bot started. Listening for commands...")
    
    # Run the bot until stopped (this will run until we get an interrupt signal)
    try:
        await application.run_polling()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error in bot loop: {e}")
    finally:
        # Shutdown scheduler
        scheduler.shutdown()
        logger.info("Scheduler shut down. Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())