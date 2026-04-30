import asyncio
import logging
from scheduler import setup_scheduler
from database import init_db

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
    
    # Keep the application running
    try:
        while True:
            await asyncio.sleep(60)  # Sleep for 60 seconds
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down gracefully...")
        scheduler.shutdown()
        logger.info("Scheduler shut down. Bot stopped.")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())