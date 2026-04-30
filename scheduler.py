import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from fetcher import fetch_all_tools, fetch_best_tool
from poster import post_morning_digest, post_evening_pick

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def morning_job():
    """Job to run every morning at 9 AM IST."""
    logger.info("Starting morning job...")
    try:
        # Fetch new tools
        tools = await fetch_all_tools()
        logger.info(f"Fetched {len(tools)} new tools for morning post")
        
        # Take first 5 tools maximum
        tools_to_post = tools[:5]
        
        # Post to channel
        await post_morning_digest(tools_to_post)
        
        logger.info(f"Morning job completed. Posted {len(tools_to_post)} tools.")
    except Exception as e:
        logger.error(f"Error in morning job: {e}")

async def evening_job():
    """Job to run every evening at 6 PM IST."""
    logger.info("Starting evening job...")
    try:
        # Fetch new tools
        tools = await fetch_all_tools()
        logger.info(f"Fetched {len(tools)} new tools for evening post")
        
        # Score tools using analyze_tool if not already scored
        # For simplicity, we'll just take the top 2 by fetching and analyzing
        # In a more complex implementation, we might check database for already scored tools
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
        top_tools = scored_tools[:2]
        
        logger.info(f"Selected top {len(top_tools)} tools for evening post")
        
        # Post to channel
        await post_evening_pick(top_tools)
        
        logger.info(f"Evening job completed. Posted {len(top_tools)} tools.")
    except Exception as e:
        logger.error(f"Error in evening job: {e}")

def setup_scheduler():
    """Set up and return the configured scheduler."""
    # Set timezone to Asia/Kolkata (IST)
    timezone = pytz.timezone("Asia/Kolkata")
    scheduler = AsyncIOScheduler(timezone=timezone)
    
    # Add morning job at 09:00 IST
    scheduler.add_job(morning_job, 'cron', hour=9, minute=0, id='morning_job')
    logger.info("Morning job scheduled for 09:00 IST")
    
    # Add evening job at 18:00 IST
    scheduler.add_job(evening_job, 'cron', hour=18, minute=0, id='evening_job')
    logger.info("Evening job scheduled for 18:00 IST")
    
    return scheduler