"""
settings.py
All bot settings in one place.

Railway Persistence Fix (Simple Version):
- Sirf 2 Railway Variables set karo:
    MORNING_POST=09:10:5   (HH:MM:MAX_TOOLS)
    EVENING_POST=18:10:2   (HH:MM:MAX_TOOLS)
- Agar set nahi hain toh runtime_settings.json fallback
- Agar woh bhi nahi toh hardcoded defaults
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

# ── Hardcoded Defaults ────────────────────────────────────────────────────────
_DEFAULT_FIRST_POST_TIME_HOUR    = 9
_DEFAULT_FIRST_POST_TIME_MINUTE  = 0
_DEFAULT_SECOND_POST_TIME_HOUR   = 18
_DEFAULT_SECOND_POST_TIME_MINUTE = 0
_DEFAULT_FIRST_MAX_TOOLS         = 5
_DEFAULT_SECOND_MAX_TOOLS        = 2

# Channel Settings
CHANNEL_ID         = "@Ai_Drop_Daily"
TIMEZONE           = "Asia/Kolkata"
POST_DELAY_SECONDS = 30

# ── Runtime Settings File ─────────────────────────────────────────────────────
_RUNTIME_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "runtime_settings.json"
)


def _load_runtime() -> dict:
    if os.path.exists(_RUNTIME_FILE):
        try:
            with open(_RUNTIME_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read runtime_settings.json: {e}")
    return {}


def save_runtime_settings():
    """Current in-memory settings disk pe save karo."""
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


# ── Parse MORNING_POST / EVENING_POST env vars ────────────────────────────────
def _parse_post_env(env_key: str):
    """
    'HH:MM:MAX' string ko parse karo.
    Returns (hour, minute, max_tools) or None if invalid/missing.
    """
    val = os.environ.get(env_key, "").strip()
    if not val:
        return None
    parts = val.split(":")
    if len(parts) != 3:
        logger.warning(f"{env_key}='{val}' invalid — expected HH:MM:MAX format")
        return None
    try:
        h, m, mx = int(parts[0]), int(parts[1]), int(parts[2])
        if not (0 <= h <= 23 and 0 <= m <= 59 and 1 <= mx <= 10):
            raise ValueError
        return h, m, mx
    except ValueError:
        logger.warning(f"{env_key}='{val}' has out-of-range values, ignoring.")
        return None


# ── Load Settings (Priority: Env > runtime_settings.json > defaults) ──────────
_saved   = _load_runtime()
_morning = _parse_post_env("MORNING_POST")
_evening = _parse_post_env("EVENING_POST")

if _morning:
    FIRST_POST_TIME_HOUR, FIRST_POST_TIME_MINUTE, FIRST_MAX_TOOLS = _morning
    logger.info(f"MORNING_POST env loaded: {FIRST_POST_TIME_HOUR:02d}:{FIRST_POST_TIME_MINUTE:02d} x{FIRST_MAX_TOOLS}")
else:
    FIRST_POST_TIME_HOUR   = _saved.get("FIRST_POST_TIME_HOUR",   _DEFAULT_FIRST_POST_TIME_HOUR)
    FIRST_POST_TIME_MINUTE = _saved.get("FIRST_POST_TIME_MINUTE", _DEFAULT_FIRST_POST_TIME_MINUTE)
    FIRST_MAX_TOOLS        = _saved.get("FIRST_MAX_TOOLS",        _DEFAULT_FIRST_MAX_TOOLS)

if _evening:
    SECOND_POST_TIME_HOUR, SECOND_POST_TIME_MINUTE, SECOND_MAX_TOOLS = _evening
    logger.info(f"EVENING_POST env loaded: {SECOND_POST_TIME_HOUR:02d}:{SECOND_POST_TIME_MINUTE:02d} x{SECOND_MAX_TOOLS}")
else:
    SECOND_POST_TIME_HOUR   = _saved.get("SECOND_POST_TIME_HOUR",   _DEFAULT_SECOND_POST_TIME_HOUR)
    SECOND_POST_TIME_MINUTE = _saved.get("SECOND_POST_TIME_MINUTE", _DEFAULT_SECOND_POST_TIME_MINUTE)
    SECOND_MAX_TOOLS        = _saved.get("SECOND_MAX_TOOLS",        _DEFAULT_SECOND_MAX_TOOLS)
