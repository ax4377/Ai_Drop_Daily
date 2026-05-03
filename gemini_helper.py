"""
gemini_helper.py
Analyzes AI tools using:
  - PRIMARY:  Groq API (ultra-fast, llama-3.3-70b-versatile)
  - FALLBACK: OpenRouter API (if Groq key missing or call fails)

Strategy:
  1. GROQ_API_KEY available → Groq se analyze karo (fast, ~1s response)
  2. Groq fail ho ya key na ho → OpenRouter pe fallback
  3. Dono fail → default dict return karo (bot kabhi crash nahi karta)
"""
import requests
import json
import logging
import time
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, GROQ_API_KEY, GROQ_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Groq ────────────────────────────────────────────────────────────────────
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── OpenRouter (fallback) ────────────────────────────────────────────────────
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://t.me/Ai_Drop_Daily",
    "X-Title": "AI Drop Daily Bot",
}


def _build_prompt(tool_name, tool_summary, tool_link):
    """Shared prompt for both Groq and OpenRouter."""
    return f"""You are an AI tools analyst. Analyze the tool below and return a JSON object.

Tool Name: {tool_name}
Tool Summary: {tool_summary}
Tool Link: {tool_link}

Return a JSON object with EXACTLY these keys:
{{
  "short_description": "2 sentences describing what this tool does. Must be complete, informative, no placeholders.",
  "use_case": "One sentence about who should use this tool. Must be specific, no placeholders.",
  "price_type": "Free or Paid only (use Free if there is any free tier)",
  "score": 8,
  "emoji": "🤖",
  "category": "One of: Image Generation, Writing, Coding, Video, Audio, Productivity, Research, Other"
}}

STRICT RULES:
- short_description and use_case must be REAL sentences, never "...", never empty
- Return ONLY the JSON object
- No markdown, no code blocks, no explanation"""


def _extract_json(text, tool_name):
    """{ ... } JSON object extract karo text se."""
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        logger.warning(f"No JSON found for {tool_name}: {text[:200]}")
        return None
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error for {tool_name}: {e}")
        return None


def _validate_result(result, default, tool_name):
    """
    Required keys check karo, placeholder values replace karo,
    aur type validations karo. Valid result return karo.
    """
    required = ["short_description", "use_case", "price_type", "score", "emoji", "category"]
    if not all(k in result for k in required):
        logger.warning(f"Missing keys for {tool_name}: {list(result.keys())}")
        return None

    # Placeholder detection
    for field in ["short_description", "use_case"]:
        val = result.get(field, "").strip()
        if val in ["...", ".", "", "N/A", "n/a"]:
            logger.warning(f"{field} is placeholder for {tool_name}, using default")
            result[field] = default[field]

    # Type validations
    if result["price_type"] not in ["Free", "Paid"]:
        result["price_type"] = "Free"
    result["score"] = max(1, min(10, int(result["score"])))
    if not result.get("category"):
        result["category"] = "Other"
    if not result.get("emoji"):
        result["emoji"] = "🤖"

    return result


def _analyze_with_groq(prompt, tool_name):
    """
    Groq API se analyze karo.
    Returns: parsed dict ya None (failure pe)
    """
    if not GROQ_API_KEY:
        logger.info("GROQ_API_KEY not set — skipping Groq")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.3,
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()

        data    = response.json()
        choices = data.get("choices", [])
        if not choices:
            logger.warning(f"Groq: no choices for {tool_name}")
            return None

        text = choices[0].get("message", {}).get("content", "")
        if not text or not text.strip():
            logger.warning(f"Groq: empty response for {tool_name}")
            return None

        logger.info(f"Groq: response received for {tool_name} ✓")
        return _extract_json(text.strip(), tool_name)

    except requests.exceptions.Timeout:
        logger.warning(f"Groq: timeout for {tool_name} — falling back to OpenRouter")
        return None
    except requests.exceptions.HTTPError as e:
        logger.warning(f"Groq: HTTP error for {tool_name}: {e} — falling back")
        return None
    except Exception as e:
        logger.warning(f"Groq: unexpected error for {tool_name}: {e} — falling back")
        return None


def _analyze_with_openrouter(prompt, tool_name):
    """
    OpenRouter API se analyze karo (fallback).
    Returns: parsed dict ya None (failure pe)
    """
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.3,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=OPENROUTER_HEADERS, json=payload, timeout=30)
        response.raise_for_status()

        data    = response.json()
        choices = data.get("choices", [])
        if not choices:
            logger.warning(f"OpenRouter: no choices for {tool_name}")
            return None

        message = choices[0].get("message", {})
        text    = message.get("content")

        # Reasoning model fallback (o1, Gemini thinking, etc.)
        if text is None:
            text = message.get("reasoning", "")
            if text:
                logger.info(f"OpenRouter: using reasoning field for {tool_name}")

        if not text or not text.strip():
            logger.warning(f"OpenRouter: empty response for {tool_name}")
            return None

        logger.info(f"OpenRouter: response received for {tool_name} ✓")
        return _extract_json(text.strip(), tool_name)

    except Exception as e:
        logger.error(f"OpenRouter: error for {tool_name}: {e}")
        return None


def analyze_tool(tool_name, tool_summary, tool_link):
    """
    AI tool ko analyze karo aur structured dict return karo.

    Flow:
      1. Groq (primary, fast)       → success? return result
      2. OpenRouter (fallback)      → success? return result
      3. Dono fail                  → default dict return karo
    """
    default = {
        "short_description": f"{tool_name} is an AI-powered tool designed to help with various tasks efficiently.",
        "use_case": "Professionals and creators looking for AI-powered solutions",
        "price_type": "Free",
        "score": 5,
        "emoji": "🤖",
        "category": "Other",
    }

    prompt = _build_prompt(tool_name, tool_summary, tool_link)

    # ── Step 1: Groq (primary) ───────────────────────────────────────────────
    raw = _analyze_with_groq(prompt, tool_name)
    if raw:
        result = _validate_result(raw, default, tool_name)
        if result:
            logger.info(f"[Groq ✓] {tool_name} — score={result['score']}, price={result['price_type']}")
            # Groq is fast — no sleep needed, but small courtesy delay
            time.sleep(0.5)
            return result
        logger.warning(f"Groq returned invalid data for {tool_name} — trying OpenRouter")

    # ── Step 2: OpenRouter (fallback) ───────────────────────────────────────
    logger.info(f"Falling back to OpenRouter for {tool_name}...")
    raw = _analyze_with_openrouter(prompt, tool_name)
    if raw:
        result = _validate_result(raw, default, tool_name)
        if result:
            logger.info(f"[OpenRouter ✓] {tool_name} — score={result['score']}, price={result['price_type']}")
            time.sleep(2)  # OpenRouter rate limit ke liye
            return result

    # ── Step 3: Both failed — return default ────────────────────────────────
    logger.error(f"Both Groq and OpenRouter failed for {tool_name} — using default")
    return default
