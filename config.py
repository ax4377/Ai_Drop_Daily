import os
from dotenv import load_dotenv
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE,
    FIRST_MAX_TOOLS, SECOND_MAX_TOOLS,
    CHANNEL_ID, TIMEZONE, POST_DELAY_SECONDS
)

# Load .env file for local development
# On Railway, environment variables are set directly in dashboard
load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = CHANNEL_ID

# Gemini settings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Timezone
TIMEZONE = TIMEZONE

# Post settings
MORNING_POST_TIME_HOUR = FIRST_POST_TIME_HOUR
MORNING_POST_TIME_MINUTE = FIRST_POST_TIME_MINUTE
EVENING_POST_TIME_HOUR = SECOND_POST_TIME_HOUR
EVENING_POST_TIME_MINUTE = SECOND_POST_TIME_MINUTE
MORNING_MAX_TOOLS = FIRST_MAX_TOOLS
EVENING_MAX_TOOLS = SECOND_MAX_TOOLS

# Validate that required keys exist
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")