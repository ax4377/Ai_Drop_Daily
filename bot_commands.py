"""
bot_commands.py
Telegram bot commands — owner only.

Fixes/additions:
- /cleardb command added (database reset when all tools become duplicates)
- /listtoday command added (aaj ke posted tools dekhne ke liye)
- /status command: ab total tools count bhi dikhata hai
- Retry logic on Telegram network errors: retained from original
- /setpost: settings.py module-level update + disk save retained
"""

import logging
import asyncio
import datetime
import pytz
import settings
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError
from scheduler import morning_job, evening_job

OWNER_ID = 1787566342

logger = logging.getLogger(__name__)


async def check_owner(update: Update) -> bool:
    """Check if the user is the bot owner."""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        logger.info(f"Unauthorized command attempt by user ID: {user_id}")
        return False
    return True


async def _safe_reply(update: Update, text: str, max_attempts: int = 3):
    """Reply with retry logic for Telegram network errors."""
    for attempt in range(max_attempts):
        try:
            await update.message.reply_text(text)
            return
        except (TimedOut, NetworkError):
            if attempt < max_attempts - 1:
                await asyncio.sleep(3)
            else:
                logger.warning(f"Reply failed after {max_attempts} attempts. Text: {text[:80]}")


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    if not await check_owner(update):
        return

    msg = (
        "🤖 Welcome to AI Drop Daily Bot Commander!\n\n"
        "Available Commands:\n"
        "/status   — Current schedule & stats\n"
        "/setpost HH:MM HH:MM max1 max2 — Change times & tool counts\n"
        "          Example: /setpost 09:10 18:10 5 2\n"
        "/testnow  — Post one tool immediately (test)\n"
        "/listtoday — Show today's posted tools\n"
        "/cleardb  — Reset duplicate database\n"
        "/help     — Show this message\n\n"
        "⚡ All changes apply instantly without restart!"
    )
    await _safe_reply(update, msg)


# ── /status ───────────────────────────────────────────────────────────────────

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    if not await check_owner(update):
        return

    from database import get_total_tools_count, get_todays_tools
    total_count  = get_total_tools_count()
    todays_count = len(get_todays_tools())

    morning_time = f"{settings.FIRST_POST_TIME_HOUR:02d}:{settings.FIRST_POST_TIME_MINUTE:02d}"
    evening_time = f"{settings.SECOND_POST_TIME_HOUR:02d}:{settings.SECOND_POST_TIME_MINUTE:02d}"

    msg = (
        f"⏰ Current Schedule:\n\n"
        f"🌅 Post 1: {morning_time} IST → {settings.FIRST_MAX_TOOLS} tools\n"
        f"🌆 Post 2: {evening_time} IST → {settings.SECOND_MAX_TOOLS} tools\n\n"
        f"📊 Stats:\n"
        f"• Today posted: {todays_count} tools\n"
        f"• Total in DB:  {total_count} tools\n\n"
        f"🟢 Bot is running!"
    )
    await _safe_reply(update, msg)


# ── /setpost ──────────────────────────────────────────────────────────────────

async def cmd_setpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /setpost command — change post times and max tools.
    Format: /setpost HH:MM HH:MM max1 max2
    Example: /setpost 09:10 18:10 5 2
    """
    if not await check_owner(update):
        return

    try:
        args = context.args

        if len(args) != 4:
            await _safe_reply(
                update,
                "❌ Galat format!\n\n"
                "✅ Sahi format:\n"
                "/setpost HH:MM HH:MM max1 max2\n\n"
                "📌 Example:\n"
                "/setpost 09:10 18:10 5 2\n\n"
                "Matlab:\n"
                "• Post 1 → 09:10 IST, 5 tools\n"
                "• Post 2 → 18:10 IST, 2 tools",
            )
            return

        # Parse time 1
        t1 = args[0].split(":")
        if len(t1) != 2:
            await _safe_reply(update, "❌ Post 1 time galat hai! HH:MM format use karo.")
            return
        hour1, minute1 = int(t1[0]), int(t1[1])

        # Parse time 2
        t2 = args[1].split(":")
        if len(t2) != 2:
            await _safe_reply(update, "❌ Post 2 time galat hai! HH:MM format use karo.")
            return
        hour2, minute2 = int(t2[0]), int(t2[1])

        max1 = int(args[2])
        max2 = int(args[3])

        # Validation
        if not (0 <= hour1 <= 23 and 0 <= minute1 <= 59):
            await _safe_reply(update, "❌ Post 1 time invalid! Hours: 0-23, Minutes: 0-59")
            return
        if not (0 <= hour2 <= 23 and 0 <= minute2 <= 59):
            await _safe_reply(update, "❌ Post 2 time invalid! Hours: 0-23, Minutes: 0-59")
            return
        if not (1 <= max1 <= 10):
            await _safe_reply(update, "❌ Post 1 max tools 1-10 ke beech hona chahiye!")
            return
        if not (1 <= max2 <= 10):
            await _safe_reply(update, "❌ Post 2 max tools 1-10 ke beech hona chahiye!")
            return

        # Update in-memory settings
        settings.FIRST_POST_TIME_HOUR    = hour1
        settings.FIRST_POST_TIME_MINUTE  = minute1
        settings.SECOND_POST_TIME_HOUR   = hour2
        settings.SECOND_POST_TIME_MINUTE = minute2
        settings.FIRST_MAX_TOOLS         = max1
        settings.SECOND_MAX_TOOLS        = max2

        # Save to disk (runtime_settings.json)
        settings.save_runtime_settings()
        logger.info("Runtime settings saved to disk.")

        # Reschedule jobs
        tz = pytz.timezone("Asia/Kolkata")

        for job_name in ["morning_job", "evening_job"]:
            for job in context.job_queue.get_jobs_by_name(job_name):
                job.schedule_removal()
            logger.info(f"Removed existing {job_name}")

        context.job_queue.run_daily(
            morning_job,
            time=datetime.time(hour=hour1, minute=minute1, tzinfo=tz),
            name="morning_job",
        )
        logger.info(f"New morning_job at {hour1:02d}:{minute1:02d} IST, max: {max1}")

        context.job_queue.run_daily(
            evening_job,
            time=datetime.time(hour=hour2, minute=minute2, tzinfo=tz),
            name="evening_job",
        )
        logger.info(f"New evening_job at {hour2:02d}:{minute2:02d} IST, max: {max2}")

        await _safe_reply(
            update,
            f"✅ Settings updated!\n\n"
            f"🌅 Post 1: {hour1:02d}:{minute1:02d} IST → {max1} tools\n"
            f"🌆 Post 2: {hour2:02d}:{minute2:02d} IST → {max2} tools\n\n"
            f"⚡ No restart needed!\n\n"
            f"💡 Tip: Railway Variables mein bhi set karo:\n"
            f"   MORNING_HOUR={hour1} MORNING_MINUTE={minute1}\n"
            f"   EVENING_HOUR={hour2} EVENING_MINUTE={minute2}\n"
            f"   MORNING_MAX_TOOLS={max1} EVENING_MAX_TOOLS={max2}\n"
            f"   (restart ke baad bhi settings yaad rahenge)",
        )

    except ValueError:
        await _safe_reply(
            update,
            "❌ Koi value galat hai!\n\n"
            "✅ Sahi format:\n"
            "/setpost 09:10 18:10 5 2\n\n"
            "• Time: HH:MM (24-hour)\n"
            "• Max tools: sirf number (1-10)",
        )
    except Exception as e:
        logger.error(f"Error in setpost: {e}", exc_info=True)
        await _safe_reply(update, f"❌ Error: {str(e)}\nRailway logs check karo.")


# ── /testnow ──────────────────────────────────────────────────────────────────

async def cmd_testnow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /testnow — post a single tool immediately for testing."""
    if not await check_owner(update):
        return

    try:
        await _safe_reply(update, "🔄 Fetching and posting test tool...")

        from fetcher import fetch_all_tools
        from poster import post_morning_digest

        tools = await fetch_all_tools()
        if tools:
            await post_morning_digest(tools[:1])
            await _safe_reply(update, "✅ Test post done! Check @Ai_Drop_Daily")
        else:
            await _safe_reply(
                update,
                "⚠️ No tools fetched.\n"
                "OpenRouter API key / model check karo.\n"
                "Agar DB full hai toh /cleardb karo.",
            )

    except Exception as e:
        logger.error(f"Error in testnow: {e}", exc_info=True)
        await _safe_reply(update, f"❌ Failed: {str(e)}\nRailway logs check karo.")


# ── /listtoday ────────────────────────────────────────────────────────────────

async def cmd_listtoday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listtoday — show today's posted tools."""
    if not await check_owner(update):
        return

    from database import get_todays_tools
    tools = get_todays_tools()

    if not tools:
        await _safe_reply(update, "📭 Aaj koi tools post nahi hue abhi tak.")
        return

    lines = [f"📋 Aaj ke posted tools ({len(tools)}):\n"]
    for i, row in enumerate(tools, 1):
        # row: (id, tool_name, tool_link, tool_description, price_type, posted_at, post_session, gemini_score)
        name    = row[1]
        session = row[6] or "?"
        score   = row[7] or "?"
        price   = row[4] or "?"
        lines.append(f"{i}. {name} | {session} | ⭐{score} | 💰{price}")

    await _safe_reply(update, "\n".join(lines))


# ── /cleardb ──────────────────────────────────────────────────────────────────

async def cmd_cleardb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /cleardb — clear the duplicate tracking database.
    Use when bot keeps saying '0 new tools' because all tools are duplicates.
    """
    if not await check_owner(update):
        return

    from database import clear_all_tools
    count = clear_all_tools()
    await _safe_reply(
        update,
        f"🗑️ Database cleared!\n"
        f"{count} tools removed.\n\n"
        f"Bot ab phir se fresh tools fetch karega.",
    )


# ── /help ─────────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    if not await check_owner(update):
        return

    msg = (
        "🤖 AI Drop Daily Bot — Commands\n\n"
        "/start   — Welcome message\n"
        "/status  — Schedule, today's count, total DB count\n"
        "/setpost HH:MM HH:MM max1 max2\n"
        "         → Example: /setpost 09:10 18:10 5 2\n"
        "/testnow — Abhi ek tool test karo\n"
        "/listtoday — Aaj ke posted tools dekho\n"
        "/cleardb — Duplicate DB reset karo\n"
        "/help    — Yeh message\n\n"
        "🔒 Sirf bot owner use kar sakta hai\n"
        "⚡ Changes turant apply hote hain!"
    )
    await _safe_reply(update, msg)
