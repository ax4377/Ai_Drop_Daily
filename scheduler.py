"""
scheduler.py
Har 2 ghante Google Sheet check karo.
Naya tool mila toh seedha post karo — koi fixed schedule nahi.
"""
import asyncio
import logging
from fetcher import fetch_all_tools
from poster import post_morning_digest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OWNER_ID = 1787566342
CHECK_INTERVAL_SECONDS = 2 * 60 * 60  # 2 ghante


async def sheet_check_job(context):
    """Har 2 ghante Google Sheet check karo — naya tool mila toh post karo."""
    logger.info("Sheet check job started...")
    try:
        tools = await fetch_all_tools()

        if not tools:
            logger.info("Koi naya tool nahi mila sheet mein. Next check 2 ghante baad.")
            return

        logger.info(f"{len(tools)} naye tools mile — posting...")
        await post_morning_digest(tools)
        logger.info(f"Posted {len(tools)} tools successfully.")

        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"✅ {len(tools)} tools posted!\nCheck @AiTool_s"
        )

    except Exception as e:
        logger.error(f"Error in sheet_check_job: {e}")
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"❌ Sheet check failed!\nError: {str(e)}"
        )


def setup_scheduler(application):
    """Har 2 ghante repeating job setup karo."""
    application.job_queue.run_repeating(
        sheet_check_job,
        interval=CHECK_INTERVAL_SECONDS,
        first=10,  # Bot start hone ke 10 second baad pehli baar check
        name="sheet_check_job"
    )
    logger.info("Sheet check job scheduled: har 2 ghante")
