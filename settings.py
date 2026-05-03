"""
settings.py
All bot settings in one place.

Railway Persistence Fix:
- Railway pe har redeploy pe fresh container milti hai
- runtime_settings.json tab bhi wipe ho jaata tha
- FIX: Settings Railway Environment Variables se load hoti hain (agar set hain)
  Railway Dashboard -> Variables mein ye set karo:
    MORNING_HOUR, MORNING_MINUTE, EVENING_HOUR, EVENING_MINUTE
    MORNING_MAX_TOOLS, EVENING_MAX_TOOLS
  Agar set nahi hain toh runtime_settings.json fallback hai
  Agar woh bhi nahi hai toh hardcoded defaults use hote hain

Order of priority:
  1. Railway Environment Variables  (restart-proof)
  2. runtime_settings.json          (same-session /setpost changes)
  3. Hardcoded defaults below
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

# ============================================
# Hardcoded Defaults
# ============================================
_DEFAULT_FIRST_POST_TIME_HOUR    = 9
_DEFAULT_FIRST_POST_TIME_MINUTE  = 0
_DEFAULT_SECOND_POST_TIME_HOUR   = 18
_DEFAULT_SECOND_POST_TIME_MINUTE = 0
_DEFAULT_FIRST_MAX_TOOLS         = 5
_DEFAULT_SECOND_MAX_TOOLS        = 2

# Channel Settings
CHANNEL_ID = "@Ai_Drop_Daily"

# Timezone
TIMEZONE = "Asia/Kolkata"

# Delay between posts (seconds)
POST_DELAY_SECONDS = 30

# ============================================
# Runtime Settings File (same-session /setpost)
# ============================================
_RUNTIME_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "runtime_settings.json"
)


def _load_runtime() -> dict:
    """runtime_settings.json se saved values load karo."""
    if os.path.exists(_RUNTIME_FILE):
        try:
            with open(_RUNTIME_FILE, "r") as f:
                data = json.load(f)
            logger.info("Loaded runtime_settings.json")
            return data
        except Exception as e:
            logger.warning(f"Could not read runtime_settings.json: {e}")
    return {}


def save_runtime_settings():
    """Current in-memory settings ko runtime_settings.json mein save karo."""
    data = {
        "FIRST_POST_TIME_HOUR":    FIRST_POST_TIME_HOUR,
        "FIRST_POST_TIME_MINUTE":  FIRST_POST_TIME_MINUTE,
        "SECOND_POST_TIME_HOUR":   SECOND_POST_TIME_HOUR,
        "SECOND_POST_TIME_MINUTE": SECOND_POST_TIME_MINUTE,
        "FIRST_MAX_TOOLS":         FIRST_MAX_TOOLS,
        "SECOND_MAX_TOOLS":        SECOND_MAX_TOOLS,
    }
    try:
        with open(_RUNTIME_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("runtime_settings.json saved.")
    except Exception as e:
        logger.error(f"Could not save runtime_settings.json: {e}")


# ============================================
# Load Settings — Priority Order
# 1. Env Vars (Railway Variables) — restart-proof
# 2. runtime_settings.json       — same-session /setpost
# 3. Hardcoded defaults
# ============================================
_saved = _load_runtime()


def _get_int(env_key: str, runtime_key: str, default: int) -> int:
    """Env var > runtime file > default."""
    env_val = os.environ.get(env_key)
    if env_val is not None:
        try:
            return int(env_val)
        except ValueError:
            logger.warning(f"Invalid env var {env_key}='{env_val}', ignoring.")
    return _saved.get(runtime_key, default)


FIRST_POST_TIME_HOUR    = _get_int("MORNING_HOUR",        "FIRST_POST_TIME_HOUR",    _DEFAULT_FIRST_POST_TIME_HOUR)
FIRST_POST_TIME_MINUTE  = _get_int("MORNING_MINUTE",      "FIRST_POST_TIME_MINUTE",  _DEFAULT_FIRST_POST_TIME_MINUTE)
SECOND_POST_TIME_HOUR   = _get_int("EVENING_HOUR",        "SECOND_POST_TIME_HOUR",   _DEFAULT_SECOND_POST_TIME_HOUR)
SECOND_POST_TIME_MINUTE = _get_int("EVENING_MINUTE",      "SECOND_POST_TIME_MINUTE", _DEFAULT_SECOND_POST_TIME_MINUTE)
FIRST_MAX_TOOLS         = _get_int("MORNING_MAX_TOOLS",   "FIRST_MAX_TOOLS",         _DEFAULT_FIRST_MAX_TOOLS)
SECOND_MAX_TOOLS        = _get_int("EVENING_MAX_TOOLS",   "SECOND_MAX_TOOLS",        _DEFAULT_SECOND_MAX_TOOLS)

logger.info(
    f"Settings loaded — Morning: {FIRST_POST_TIME_HOUR:02d}:{FIRST_POST_TIME_MINUTE:02d} "
    f"({FIRST_MAX_TOOLS} tools) | Evening: {SECOND_POST_TIME_HOUR:02d}:{SECOND_POST_TIME_MINUTE:02d} "
    f"({SECOND_MAX_TOOLS} tools)"
)
