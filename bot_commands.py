import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE
)

# Import scheduler jobs for rescheduling
from scheduler import morning_job, evening_job

# Owner ID - only this user can use commands
OWNER_ID = 1787566342

async def check_owner(update: Update) -> bool:
    """Check if the user is the bot owner"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        logging.info(f"Unauthorized command attempt by user ID: {user_id}")
        return False
    return True

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message"""
    if not await check_owner(update):
        return

    welcome_message = """
🤖 Welcome to AI Drop Daily Bot Commander!

Available Commands:
/status - Check current post times and bot status
/settime HH:MM HH:MM - Set new post times (e.g., /settime 09:00 18:00)
/testnow - Post a test AI tool right now
/help - Show this help message

All commands work instantly without restart!
    """
    await update.message.reply_text(welcome_message.strip())

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show current schedule"""
    if not await check_owner(update):
        return

    # Get current scheduled jobs
    current_jobs = context.job_queue.jobs()
    morning_time = f"{FIRST_POST_TIME_HOUR:02d}:{FIRST_POST_TIME_MINUTE:02d}"
    evening_time = f"{SECOND_POST_TIME_HOUR:02d}:{SECOND_POST_TIME_MINUTE:02d}"

    for job in current_jobs:
        if job.name == "morning_job" and hasattr(job, 'next_t'):
            try:
                tz = pytz.timezone("Asia/Kolkata")
                t = job.next_t.astimezone(tz)
                morning_time = f"{t.hour:02d}:{t.minute:02d}"
            except Exception:
                pass
        if job.name == "evening_job" and hasattr(job, 'next_t'):
            try:
                tz = pytz.timezone("Asia/Kolkata")
                t = job.next_t.astimezone(tz)
                evening_time = f"{t.hour:02d}:{t.minute:02d}"
            except Exception:
                pass

    status_message = f"""
⏰ Current Schedule:
🌅 First Post: {morning_time} IST
🌆 Second Post: {evening_time} IST
🟢 Bot is running!
    """
    await update.message.reply_text(status_message.strip())

async def cmd_settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settime command - change post times instantly"""
    if not await check_owner(update):
        return

    try:
        # Get arguments
        args = context.args
        if len(args) != 2:
            await update.message.reply_text(
                "❌ Usage: /settime HH:MM HH:MM\n"
                "Example: /settime 09:00 18:00"
            )
            return

        # Parse first time
        time1_parts = args[0].split(':')
        if len(time1_parts) != 2:
            await update.message.reply_text("❌ Invalid format! Use HH:MM\nExample: /settime 09:00 18:00")
            return
        hour1 = int(time1_parts[0])
        minute1 = int(time1_parts[1])

        # Parse second time
        time2_parts = args[1].split(':')
        if len(time2_parts) != 2:
            await update.message.reply_text("❌ Invalid format! Use HH:MM\nExample: /settime 09:00 18:00")
            return
        hour2 = int(time2_parts[0])
        minute2 = int(time2_parts[1])

        # Validate ranges
        if not (0 <= hour1 <= 23 and 0 <= minute1 <= 59):
            await update.message.reply_text("❌ First time invalid! Hours: 0-23, Minutes: 0-59")
            return
        if not (0 <= hour2 <= 23 and 0 <= minute2 <= 59):
            await update.message.reply_text("❌ Second time invalid! Hours: 0-23, Minutes: 0-59")
            return

        # Timezone
        tz = pytz.timezone("Asia/Kolkata")

        # Remove existing morning and evening jobs safely
        for job_name in ["morning_job", "evening_job"]:
            jobs = context.job_queue.get_jobs_by_name(job_name)
            for job in jobs:
                job.schedule_removal()
            logging.info(f"Removed existing {job_name}")

        # Add new morning job
        context.job_queue.run_daily(
            morning_job,
            time=datetime.time(hour=hour1, minute=minute1, tzinfo=tz),
            name="morning_job"
        )
        logging.info(f"New morning_job scheduled at {hour1:02d}:{minute1:02d} IST")

        # Add new evening job
        context.job_queue.run_daily(
            evening_job,
            time=datetime.time(hour=hour2, minute=minute2, tzinfo=tz),
            name="evening_job"
        )
        logging.info(f"New evening_job scheduled at {hour2:02d}:{minute2:02d} IST")

        # Log the change
        logging.info(f"Post times updated by owner: {hour1:02d}:{minute1:02d} and {hour2:02d}:{minute2:02d}")

        # Send confirmation
        confirmation_message = f"""
✅ Times updated instantly!

🌅 First Post: {hour1:02d}:{minute1:02d} IST
🌆 Second Post: {hour2:02d}:{minute2:02d} IST

⚡ No restart needed!
        """
        await update.message.reply_text(confirmation_message.strip())

    except ValueError as e:
        await update.message.reply_text(
            f"❌ Invalid time: {str(e)}\n"
            "Use HH:MM format (24-hour)\n"
            "Example: /settime 09:00 18:00"
        )
    except Exception as e:
        logging.error(f"Error in settime command: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n"
            "Check Railway logs for details."
        )

async def cmd_testnow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /testnow command - post a test tool immediately"""
    if not await check_owner(update):
        return

    try:
        await update.message.reply_text("🔄 Posting test now...")

        # Import required functions
        from fetcher import fetch_all_tools
        from poster import post_morning_digest

        # Fetch one tool and post it
        tools = await fetch_all_tools()
        if tools:
            await post_morning_digest(tools[:1])
            await update.message.reply_text("✅ Test post done! Check @Ai_Drop_Daily")
        else:
            await update.message.reply_text("⚠️ No tools fetched. Check Gemini API key.")

    except Exception as e:
        logging.error(f"Error in testnow command: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Failed: {str(e)}\n"
            "Check Railway logs for details."
        )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show all commands"""
    if not await check_owner(update):
        return

    help_message = """
🤖 AI Drop Daily Bot - Command Help

/start - Show welcome message
/status - Show current post times and bot status
/settime HH:MM HH:MM - Set new post times
    Example: /settime 09:00 18:00
/testnow - Post a test AI tool right now
/help - Show this help message

🔒 Only bot owner can use these commands
⚡ Changes apply instantly - no restart needed!
    """
    await update.message.reply_text(help_message.strip())
