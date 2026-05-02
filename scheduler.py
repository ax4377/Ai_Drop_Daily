import asyncio
import logging
import datetime
import pytz
from fetcher import fetch_all_tools, fetch_best_tool
from poster import post_morning_digest, post_evening_pick
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OWNER_ID = 1787566342


async def morning_job(context):
    """Morning post — fetch tools and post directly. No pre-scoring needed."""
    logger.info("Starting morning job...")
    try:
        tools = await fetch_all_tools()
        logger.info(f"Fetched {len(tools)} new tools for morning post")

        import settings
        tools_to_post = tools[:settings.FIRST_MAX_TOOLS]

        await post_morning_digest(tools_to_post)
        logger.info(f"Morning job completed. Posted {len(tools_to_post)} tools.")

        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"✅ Post 1 done! {len(tools_to_post)} tools posted.\nCheck @Ai_Drop_Daily"
        )

    except Exception as e:
        logger.error(f"Error in morning job: {e}")
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"❌ Post 1 failed!\nError: {str(e)}"
        )


async def evening_job(context):
    """Evening post — fetch, score once, cache analysis, post top tools.
    analyze_tool is called ONCE here for scoring+caching.
    poster.py reuses _cached_analysis — no double API call.
    """
    logger.info("Starting evening job...")
    try:
        tools = await fetch_all_tools()
        logger.info(f"Fetched {len(tools)} tools for evening post")

        from gemini_helper import analyze_tool
        scored_tools = []

        for tool in tools:
            try:
                tool_info = analyze_tool(tool["name"], tool["summary"], tool["link"])
                tool_copy = tool.copy()
                tool_copy["_cached_analysis"] = tool_info  # poster.py reuse karega
                tool_copy["score"] = tool_info["score"]
                scored_tools.append(tool_copy)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error scoring tool {tool['name']}: {e}")
                tool_copy = tool.copy()
                tool_copy["score"] = 5
                scored_tools.append(tool_copy)

        scored_tools.sort(key=lambda x: x["score"], reverse=True)

        import settings
        top_tools = scored_tools[:settings.SECOND_MAX_TOOLS]
        logger.info(f"Selected top {len(top_tools)} tools for evening post")

        await post_evening_pick(top_tools)
        logger.info(f"Evening job completed. Posted {len(top_tools)} tools.")

        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"✅ Post 2 done! {len(top_tools)} tools posted.\nCheck @Ai_Drop_Daily"
        )

    except Exception as e:
        logger.error(f"Error in evening job: {e}")
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"❌ Post 2 failed!\nError: {str(e)}"
        )


def setup_scheduler(application):
    """Setup daily jobs using telegram job queue."""
    tz = pytz.timezone("Asia/Kolkata")

    application.job_queue.run_daily(
        morning_job,
        time=datetime.time(hour=FIRST_POST_TIME_HOUR, minute=FIRST_POST_TIME_MINUTE, tzinfo=tz),
        name="morning_job"
    )
    logger.info(f"Morning job scheduled: {FIRST_POST_TIME_HOUR:02d}:{FIRST_POST_TIME_MINUTE:02d} IST")

    application.job_queue.run_daily(
        evening_job,
        time=datetime.time(hour=SECOND_POST_TIME_HOUR, minute=SECOND_POST_TIME_MINUTE, tzinfo=tz),
        name="evening_job"
    )
    logger.info(f"Evening job scheduled: {SECOND_POST_TIME_HOUR:02d}:{SECOND_POST_TIME_MINUTE:02d} IST")
