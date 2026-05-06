import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

OWNER_ID = 1787566342


async def check_owner(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        logging.info(f"Unauthorized command attempt by user ID: {user_id}")
        return False
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_owner(update):
        return
    welcome_message = """
🤖 Welcome to AI Drop Daily Bot!

Available Commands:
/status - Bot ka status dekho
/testnow - Abhi Google Sheet check karo aur post karo
/help - Help message

Bot har 2 ghante automatically Google Sheet check karta hai.
Naya tool mila toh seedha channel pe post ho jaata hai!
    """
    await update.message.reply_text(welcome_message.strip())


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_owner(update):
        return
    status_message = """
🟢 Bot is running!

⏰ Check Interval: Har 2 ghante
📊 Source: Google Sheets
📢 Channel: @AiTool_s

Naya tool sheet mein add karo — bot automatically post kar dega!
    """
    await update.message.reply_text(status_message.strip())


async def cmd_testnow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Abhi sheet check karo aur tools post karo."""
    if not await check_owner(update):
        return
    try:
        await update.message.reply_text("🔄 Google Sheet check ho raha hai...")

        from fetcher import fetch_all_tools
        from poster import post_morning_digest

        tools = await fetch_all_tools()
        if tools:
            await post_morning_digest(tools)
            for attempt in range(3):
                try:
                    await update.message.reply_text(
                        f"✅ {len(tools)} tools posted! Check @AiTool_s"
                    )
                    break
                except (TimedOut, NetworkError):
                    if attempt < 2:
                        await asyncio.sleep(3)
        else:
            await update.message.reply_text(
                "⚠️ Koi naya tool nahi mila!\n"
                "Sheet mein aaj ki date ke saath tools add karo."
            )

    except Exception as e:
        logging.error(f"Error in testnow command: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Failed: {str(e)}\nRailway logs check karo."
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_owner(update):
        return
    help_message = """
🤖 AI Drop Daily Bot - Help

/start - Welcome message
/status - Bot status dekho
/testnow - Abhi sheet check karo aur post karo
/help - Yeh message

🔒 Sirf bot owner use kar sakta hai
⏰ Auto check: Har 2 ghante
    """
    await update.message.reply_text(help_message.strip())
