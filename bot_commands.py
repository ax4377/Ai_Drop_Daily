import logging
import asyncio
import datetime
import pytz
import settings  # Dynamic update ke liye module import
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

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
/setpost HH:MM HH:MM max1 max2 - Set times and tool counts
    Example: /setpost 09:10 15:10 2 3
/testnow - Post a test AI tool right now
/help - Show this help message

All commands work instantly without restart!
    """
    await update.message.reply_text(welcome_message.strip())


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show current schedule"""
    if not await check_owner(update):
        return

    morning_time = f"{settings.FIRST_POST_TIME_HOUR:02d}:{settings.FIRST_POST_TIME_MINUTE:02d}"
    evening_time = f"{settings.SECOND_POST_TIME_HOUR:02d}:{settings.SECOND_POST_TIME_MINUTE:02d}"
    max1 = settings.FIRST_MAX_TOOLS
    max2 = settings.SECOND_MAX_TOOLS

    status_message = f"""
⏰ Current Schedule:

🌅 Post 1: {morning_time} IST → {max1} tools
🌆 Post 2: {evening_time} IST → {max2} tools

🟢 Bot is running!
    """
    await update.message.reply_text(status_message.strip())


async def cmd_setpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /setpost command - change post times and max tools count.

    Format: /setpost HH:MM HH:MM max1 max2
    Example: /setpost 09:10 15:10 2 3
    """
    if not await check_owner(update):
        return

    try:
        args = context.args

        if len(args) != 4:
            await update.message.reply_text(
                "❌ Galat format!\n\n"
                "✅ Sahi format:\n"
                "/setpost HH:MM HH:MM max1 max2\n\n"
                "📌 Example:\n"
                "/setpost 09:10 15:10 2 3\n\n"
                "Matlab:\n"
                "• Post 1 → 09:10 IST, 2 tools\n"
                "• Post 2 → 15:10 IST, 3 tools"
            )
            return

        # Time 1 parse
        time1_parts = args[0].split(':')
        if len(time1_parts) != 2:
            await update.message.reply_text("❌ Post 1 time galat hai! HH:MM format use karo.")
            return
        hour1 = int(time1_parts[0])
        minute1 = int(time1_parts[1])

        # Time 2 parse
        time2_parts = args[1].split(':')
        if len(time2_parts) != 2:
            await update.message.reply_text("❌ Post 2 time galat hai! HH:MM format use karo.")
            return
        hour2 = int(time2_parts[0])
        minute2 = int(time2_parts[1])

        # Max tools parse
        max1 = int(args[2])
        max2 = int(args[3])

        # Validation
        if not (0 <= hour1 <= 23 and 0 <= minute1 <= 59):
            await update.message.reply_text("❌ Post 1 time invalid! Hours: 0-23, Minutes: 0-59")
            return
        if not (0 <= hour2 <= 23 and 0 <= minute2 <= 59):
            await update.message.reply_text("❌ Post 2 time invalid! Hours: 0-23, Minutes: 0-59")
            return
        if not (1 <= max1 <= 10):
            await update.message.reply_text("❌ Post 1 max tools 1-10 ke beech hona chahiye!")
            return
        if not (1 <= max2 <= 10):
            await update.message.reply_text("❌ Post 2 max tools 1-10 ke beech hona chahiye!")
            return

        # Settings module dynamically update karo
        settings.FIRST_POST_TIME_HOUR = hour1
        settings.FIRST_POST_TIME_MINUTE = minute1
        settings.SECOND_POST_TIME_HOUR = hour2
        settings.SECOND_POST_TIME_MINUTE = minute2
        settings.FIRST_MAX_TOOLS = max1
        settings.SECOND_MAX_TOOLS = max2

        # Disk pe save karo taaki restart ke baad bhi rahein
        settings.save_runtime_settings()
        logging.info("Runtime settings saved to disk.")

        # Timezone
        tz = pytz.timezone("Asia/Kolkata")

        # Purane jobs remove karo
        for job_name in ["morning_job", "evening_job"]:
            jobs = context.job_queue.get_jobs_by_name(job_name)
            for job in jobs:
                job.schedule_removal()
            logging.info(f"Removed existing {job_name}")

        # Naye jobs schedule karo
        context.job_queue.run_daily(
            morning_job,
            time=datetime.time(hour=hour1, minute=minute1, tzinfo=tz),
            name="morning_job"
        )
        logging.info(f"New morning_job at {hour1:02d}:{minute1:02d} IST, max: {max1}")

        context.job_queue.run_daily(
            evening_job,
            time=datetime.time(hour=hour2, minute=minute2, tzinfo=tz),
            name="evening_job"
        )
        logging.info(f"New evening_job at {hour2:02d}:{minute2:02d} IST, max: {max2}")

        confirmation_message = f"""
✅ Settings updated instantly!

🌅 Post 1: {hour1:02d}:{minute1:02d} IST → {max1} tools
🌆 Post 2: {hour2:02d}:{minute2:02d} IST → {max2} tools

⚡ No restart needed!
        """
        # Retry logic — busy hone par timeout aa sakta hai, 3 baar try karo
        for attempt in range(3):
            try:
                await update.message.reply_text(confirmation_message.strip())
                break
            except (TimedOut, NetworkError):
                if attempt < 2:
                    await asyncio.sleep(3)
                else:
                    # Teeno baar fail — silently log karo, settings already save ho chuki hain
                    logging.warning("setpost: confirmation reply timeout after 3 attempts. Settings were saved.")

    except ValueError:
        await update.message.reply_text(
            "❌ Koi value galat hai!\n\n"
            "✅ Sahi format:\n"
            "/setpost 09:10 15:10 2 3\n\n"
            "• Time: HH:MM (24-hour)\n"
            "• Max tools: sirf number (1-10)"
        )
    except Exception as e:
        logging.error(f"Error in setpost command: {e}", exc_info=True)
        # Reply bhi retry karo exception case mein
        for attempt in range(3):
            try:
                await update.message.reply_text(
                    f"❌ Error: {str(e)}\n"
                    "Railway logs check karo."
                )
                break
            except (TimedOut, NetworkError):
                if attempt < 2:
                    await asyncio.sleep(3)


async def cmd_testnow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /testnow command - post a test tool immediately"""
    if not await check_owner(update):
        return

    try:
        await update.message.reply_text("🔄 Posting test now...")

        from fetcher import fetch_all_tools
        from poster import post_morning_digest

        tools = await fetch_all_tools()
        if tools:
            await post_morning_digest(tools[:1])
            await update.message.reply_text("✅ Test post done! Check @Ai_Drop_Daily")
        else:
            await update.message.reply_text("⚠️ No tools fetched. OpenRouter API key / model check karo.")

    except Exception as e:
        logging.error(f"Error in testnow command: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Failed: {str(e)}\n"
            "Railway logs check karo."
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not await check_owner(update):
        return

    help_message = """
🤖 AI Drop Daily Bot - Command Help

/start - Welcome message
/status - Current schedule aur tool counts dekho
/setpost HH:MM HH:MM max1 max2
    → Times aur max tools ek saath set karo
    → Example: /setpost 09:10 15:10 2 3
    → Post 1: 09:10 IST, 2 tools
    → Post 2: 15:10 IST, 3 tools
/testnow - Abhi ek tool test karo
/help - Yeh message

🔒 Sirf bot owner use kar sakta hai
⚡ Changes turant apply hote hain!
    """
    await update.message.reply_text(help_message.strip())
