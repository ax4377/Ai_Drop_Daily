import os
from dotenv import load_dotenv
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE,
    FIRST_MAX_TOOLS, SECOND_MAX_TOOLS,
    CHANNEL_ID, TIMEZONE, POST_DELAY_SECONDS
)

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = CHANNEL_ID

# OpenRouter — tool fetching + analysis (fallback for analyzer)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# OpenRouter model — change anytime from Railway variables
# Default: google/gemini-2.5-flash
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")

# Groq — primary analyzer (faster, free tier generous)
# Get key from: https://console.groq.com/keys
# Default model: llama-3.3-70b-versatile (best JSON accuracy on Groq)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Timezone & schedule
TIMEZONE = TIMEZONE
MORNING_POST_TIME_HOUR   = FIRST_POST_TIME_HOUR
MORNING_POST_TIME_MINUTE = FIRST_POST_TIME_MINUTE
EVENING_POST_TIME_HOUR   = SECOND_POST_TIME_HOUR
EVENING_POST_TIME_MINUTE = SECOND_POST_TIME_MINUTE
MORNING_MAX_TOOLS = FIRST_MAX_TOOLS
EVENING_MAX_TOOLS = SECOND_MAX_TOOLS

# Validate
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set!")
