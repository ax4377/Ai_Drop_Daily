import os
from dotenv import load_dotenv

# Load .env file for local development
# On Railway, environment variables are set directly in dashboard
load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = "@Ai_Drop_Daily"

# Gemini settings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Timezone
TIMEZONE = "Asia/Kolkata"

# Post settings
MORNING_POST_TIME = "09:00"
EVENING_POST_TIME = "18:00"
MORNING_MAX_TOOLS = 5
EVENING_MAX_TOOLS = 2

# Validate that required keys exist
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")