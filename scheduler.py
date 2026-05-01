import logging
import datetime
import pytz
from fetcher import fetch_all_tools, fetch_best_tool
from poster import post_morning_digest, post_evening_pick
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE,
    FIRST_MAX_TOOLS, SECOND_MAX_TOOLS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def morning_job(context):
    """Job to run every morning at configured IST time."""
    logger.info("Starting morning job...")
    try:
        # Fetch new tools
        tools = await fetch_all_tools()
        logger.info(f"Fetched {len(tools)} new tools for morning post")
        
        # Take first 5 tools maximum
        tools_to_post = tools[:FIRST_MAX_TOOLS]
        
        # Post to channel
        await post_morning_digest(tools_to_post)
        
        logger.info(f"Morning job completed. Posted {len(tools_to_post)} tools.")
    except Exception as e:
        logger.error(f"Error in morning job: {e}")

async def evening_job(context):
    """Job to run every evening at configured IST time."""
    logger.info("Starting evening job...")
    try:
        # Fetch new tools
        tools = await fetch_all_tools()
        logger.info(f"Fetched {len(tools)} new tools for evening post")
        
        # Score tools using analyze_tool if not already scored
        scored_tools = []
        from gemini_helper import analyze_tool
        
        for tool in tools:
            try:
                # Analyze the tool to get score
                tool_info = analyze_tool(tool['name'], tool['summary'], tool['link'])
                tool_with_score = tool.copy()
                tool_with_score['score'] = tool_info['score']
                scored_tools.append(tool_with_score)
                # Small delay to avoid rate limiting
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error scoring tool {tool['name']}: {e}")
                # Still add the tool with a default score
                tool_with_score = tool.copy()
                tool_with_score['score'] = 5
                scored_tools.append(tool_with_score)
        
        # Sort by score descending and pick top 2
        scored_tools.sort(key=lambda x: x['score'], reverse=True)
        top_tools = scored_tools[:SECOND_MAX_TOOLS]
        
        logger.info(f"Selected top {len(top_tools)} tools for evening post")
        
        # Post to channel
        await post_evening_pick(top_tools)
        
        logger.info(f"Evening job completed. Posted {len(top_tools)} tools.")
    except Exception as e:
        logger.error(f"Error in evening job: {e}")

def setup_scheduler(application):
    """Setup scheduler using the application's job queue."""
    import pytz
    from telegram.ext import JobQueue
    tz = pytz.timezone("Asia/Kolkata")
    
    # Schedule morning job
    application.job_queue.run_daily(
        morning_job,
        time=datetime.time(
            hour=FIRST_POST_TIME_HOUR,
            minute=FIRST_POST_TIME_MINUTE,
            tzinfo=tz
        ),
        name="morning_job"
    )
    logger.info(f"Morning job scheduled for {FIRST_POST_TIME_HOUR:02d}:{FIRST_POST_TIME_MINUTE:02d} IST")
    
    # Schedule evening job
    application.job_queue.run_daily(
        evening_job,
        time=datetime.time(
            hour=SECOND_POST_TIME_HOUR,
            minute=SECOND_POST_TIME_MINUTE,
            tzinfo=tz
        ),
        name="evening_job"
    )
    logger.info(f"Evening job scheduled for {SECOND_POST_TIME_HOUR:02d}:{SECOND_POST_TIME_MINUTE:02d} IST")