import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = "@Ai_Drop_Daily"

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Timezone and scheduling
TIMEZONE = "Asia/Kolkata"
MORNING_POST_TIME = "09:00"
EVENING_POST_TIME = "18:00"

# Posting limits
MORNING_MAX_TOOLS = 5
EVENING_MAX_TOOLS = 2