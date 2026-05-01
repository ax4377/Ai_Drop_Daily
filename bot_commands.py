import logging
from telegram import Update
from telegram.ext import ContextTypes
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE
)
from scheduler import scheduler_instance

# Owner ID - only this user can use commands
OWNER_ID = 1787566342

async def check_owner(update: Update) -> bool:
    """Check if the user is the bot owner"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        logging.info(f"Unauthorized command attempt by user ID: {user_id}")
        return False
    return True

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show current schedule"""
    if not await check_owner(update):
        return
    
    status_message = f"""
⏰ Current Schedule:
First Post: {FIRST_POST_TIME_HOUR:02d}:{FIRST_POST_TIME_MINUTE:02d} IST
Second Post: {SECOND_POST_TIME_HOUR:02d}:{SECOND_POST_TIME_MINUTE:02d} IST
🟢 Bot is running!
    """
    await update.message.reply_text(status_message.strip())

async def settime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settime command - change post times"""
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
            raise ValueError("Invalid time format")
        hour1 = int(time1_parts[0])
        minute1 = int(time1_parts[1])
        
        # Parse second time
        time2_parts = args[1].split(':')
        if len(time2_parts) != 2:
            raise ValueError("Invalid time format")
        hour2 = int(time2_parts[0])
        minute2 = int(time2_parts[1])
        
        # Validate ranges
        if not (0 <= hour1 <= 23 and 0 <= minute1 <= 59):
            raise ValueError("First time: Hours 0-23, Minutes 0-59")
        if not (0 <= hour2 <= 23 and 0 <= minute2 <= 59):
            raise ValueError("Second time: Hours 0-23, Minutes 0-59")
        
        # Remove existing jobs
        scheduler_instance.remove_job('morning_job')
        scheduler_instance.remove_job('evening_job')
        
        # Add new jobs with updated times
        scheduler_instance.add_job(
            morning_job, 'cron', 
            hour=hour1, minute=minute1, 
            id='morning_job'
        )
        scheduler_instance.add_job(
            evening_job, 'cron', 
            hour=hour2, minute=minute2, 
            id='evening_job'
        )
        
        # Log the change
        logging.info(f"Post times updated by owner: {hour1:02d}:{minute1:02d} and {hour2:02d}:{minute2:02d}")
        
        # Send confirmation
        confirmation_message = f"""
✅ Times updated instantly!
First Post: {hour1:02d}:{minute1:02d} IST
Second Post: {hour2:02d}:{minute2:02d} IST
No restart needed!
        """
        await update.message.reply_text(confirmation_message.strip())
        
    except ValueError as e:
        await update.message.reply_text(
            f"❌ Invalid time format: {str(e)}\n"
            "Please use HH:MM format (24-hour clock)\n"
            "Example: /settime 09:00 18:00"
        )
    except Exception as e:
        logging.error(f"Error in settime command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while updating times. Please try again."
        )

async def testnow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        logging.error(f"Error in testnow command: {e}")
        await update.message.reply_text(
            "❌ Failed to post test tool. Check logs for details."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show all commands"""
    if not await check_owner(update):
        return
    
    help_message = """
🤖 AI Drop Daily Bot - Command Help

/start - Show welcome message and available commands
/status - Show current post times and bot status
/settime HH:MM HH:MM - Set new post times (e.g., /settime 09:00 18:00)
/testnow - Post a test AI tool right now
/help - Show this help message

🔒 Security: Only bot owner (ID: 1787566342) can use these commands
⚡ Changes apply instantly - no restart needed!
    """
    await update.message.reply_text(help_message.strip())