"""
config.py
Environment variable loader.

Fixes applied:
- GEMINI_IMAGE_API_KEY removed (dead variable — code mein use nahi hota)
- TELEGRAM_CHANNEL_ID ab CHANNEL_ID se aata hai (poster.py mein hardcode tha)
- Saari config values ek jagah
"""

import os
from dotenv import load_dotenv
from settings import (
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE,
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE,
    FIRST_MAX_TOOLS, SECOND_MAX_TOOLS,
    CHANNEL_ID, TIMEZONE, POST_DELAY_SECONDS,
)

load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = CHANNEL_ID   # poster.py yahan se lega, hardcode nahi hoga

# ── OpenRouter ────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Default model: gemini-2.5-flash (better quality than free models)
# Free models jaise gpt-oss-120b:free hallucinated/fake tool names dete hain
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")

# ── Schedule ──────────────────────────────────────────────────────────────────
TIMEZONE                 = TIMEZONE
MORNING_POST_TIME_HOUR   = FIRST_POST_TIME_HOUR
MORNING_POST_TIME_MINUTE = FIRST_POST_TIME_MINUTE
EVENING_POST_TIME_HOUR   = SECOND_POST_TIME_HOUR
EVENING_POST_TIME_MINUTE = SECOND_POST_TIME_MINUTE
MORNING_MAX_TOOLS        = FIRST_MAX_TOOLS
EVENING_MAX_TOOLS        = SECOND_MAX_TOOLS

# ── Validation ────────────────────────────────────────────────────────────────
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set!")
