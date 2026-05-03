# ============================================
# AI Drop Daily Bot — All Settings Here
# Change anything here, bot will follow!
# ============================================

import json
import os

# Default Values (settings.py ke defaults — pehli baar ya reset ke liye)
_DEFAULT_FIRST_POST_TIME_HOUR   = 9
_DEFAULT_FIRST_POST_TIME_MINUTE = 0
_DEFAULT_SECOND_POST_TIME_HOUR  = 18
_DEFAULT_SECOND_POST_TIME_MINUTE = 0
_DEFAULT_FIRST_MAX_TOOLS  = 5
_DEFAULT_SECOND_MAX_TOOLS = 2

# Runtime settings file — Railway pe /tmp mein save hota hai (restart-proof nahi)
# Isliye same directory mein save karte hain
_RUNTIME_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime_settings.json")


def _load_runtime():
    """runtime_settings.json se saved values load karo. File nahi hai toh defaults use karo."""
    if os.path.exists(_RUNTIME_FILE):
        try:
            with open(_RUNTIME_FILE, "r") as f:
                data = json.load(f)
            return data
        except Exception:
            pass
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
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Could not save runtime settings: {e}")


# Startup pe saved values load karo (ya defaults use karo)
_saved = _load_runtime()

FIRST_POST_TIME_HOUR    = _saved.get("FIRST_POST_TIME_HOUR",    _DEFAULT_FIRST_POST_TIME_HOUR)
FIRST_POST_TIME_MINUTE  = _saved.get("FIRST_POST_TIME_MINUTE",  _DEFAULT_FIRST_POST_TIME_MINUTE)
SECOND_POST_TIME_HOUR   = _saved.get("SECOND_POST_TIME_HOUR",   _DEFAULT_SECOND_POST_TIME_HOUR)
SECOND_POST_TIME_MINUTE = _saved.get("SECOND_POST_TIME_MINUTE", _DEFAULT_SECOND_POST_TIME_MINUTE)
FIRST_MAX_TOOLS         = _saved.get("FIRST_MAX_TOOLS",         _DEFAULT_FIRST_MAX_TOOLS)
SECOND_MAX_TOOLS        = _saved.get("SECOND_MAX_TOOLS",        _DEFAULT_SECOND_MAX_TOOLS)

# Channel Settings
CHANNEL_ID = "@Ai_Drop_Daily"

# Timezone
TIMEZONE = "Asia/Kolkata"

# Delay between posts (seconds)
POST_DELAY_SECONDS = 30
