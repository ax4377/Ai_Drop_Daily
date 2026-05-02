"""
fetcher.py
Fetches trending AI tools using OpenRouter API (OpenAI-compatible).
"""
import requests
import json
import logging
import time
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from database import is_duplicate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://t.me/Ai_Drop_Daily",
    "X-Title": "AI Drop Daily Bot",
}
MODEL = OPENROUTER_MODEL


def _call_openrouter(prompt: str, max_tokens: int = 4000) -> str:
    """Send a prompt to OpenRouter and return response text."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    choices = data.get("choices")
    if not choices:
        logger.error(f"OpenRouter response missing choices: {data}")
        raise ValueError(f"No choices in response")

    message = choices[0].get("message", {})
    finish_reason = choices[0].get("finish_reason", "unknown")

    # Normal content check
    text = message.get("content")

    # Reasoning model fallback — content None hota hai, reasoning mein hota hai
    if text is None:
        reasoning = message.get("reasoning")
        if reasoning:
            logger.warning(f"Content is None, extracting from reasoning field (finish_reason: {finish_reason})")
            text = reasoning
        else:
            logger.error(f"Both content and reasoning are None. finish_reason={finish_reason}. Full: {data}")
            raise ValueError(f"No content or reasoning in response. finish_reason={finish_reason}")

    if not text or not text.strip():
        raise ValueError(f"Empty response from OpenRouter. finish_reason={finish_reason}")

    return text.strip()


def validate_tools_list(tools):
    if not tools:
        return []
    valid = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        name    = tool.get("name", "").strip()
        link    = tool.get("link", "").strip()
        summary = tool.get("summary", "").strip()
        if not name or not link or not summary:
            continue
        if not link.startswith("http"):
            continue
        valid.append(tool)
    removed = len(tools) - len(valid)
    if removed:
        logger.info(f"Removed {removed} invalid tools during validation")
    return valid


async def fetch_all_tools():
    """Fetch 15 recently launched or trending AI tools via OpenRouter."""
    try:
        logger.info(f"Fetching AI tools via OpenRouter ({MODEL})...")

        prompt = """You are an AI tools researcher with up-to-date knowledge of 2025-2026.
Give me a list of 15 recently launched or currently trending AI tools.
Return ONLY a valid JSON array — no markdown, no code blocks, no extra text.
Each object must have exactly these keys:
  name        (string)
  link        (string, real working URL)
  summary     (string, 2-3 lines)
  price_type  (string, one of: Free, Freemium, Paid)
  category    (string, e.g. Image Generation, Writing, Coding, Video, Audio, Productivity, Research)
Return exactly 15 tools."""

        text = _call_openrouter(prompt)
        time.sleep(1)

        start = text.find("[")
        end   = text.rfind("]") + 1
        if start == -1 or end == 0:
            logger.warning(f"No JSON array found: {text[:200]}")
            return []

        tools = json.loads(text[start:end])
        if not isinstance(tools, list):
            logger.error("Response is not a list")
            return []

        logger.info(f"OpenRouter returned {len(tools)} tools")
        tools = validate_tools_list(tools)

        new_tools = [t for t in tools if not is_duplicate(t["link"])]
        logger.info(f"{len(new_tools)} new tools after duplicate filter")

        if len(new_tools) < 5:
            logger.warning(f"Only {len(new_tools)} new tools found")

        return new_tools

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching tools via OpenRouter: {e}")
        return []


async def fetch_best_tool():
    """Fetch the single most impressive AI tool via OpenRouter."""
    try:
        logger.info(f"Fetching best AI tool via OpenRouter ({MODEL})...")

        prompt = """You are an AI tools researcher with up-to-date knowledge of 2025-2026.
What is the single most impressive and useful AI tool launched or updated in 2025-2026?
Return ONLY a valid JSON object — no markdown, no code blocks, no extra text.
Required keys:
  name       (string)
  link       (string, real working URL)
  summary    (string, 3-4 lines)
  price_type (string, one of: Free, Freemium, Paid)
  category   (string)
  why_best   (string, 1-2 lines why it stands out)"""

        text = _call_openrouter(prompt)
        time.sleep(1)

        start = text.find("{")
        end   = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object in response")

        tool = json.loads(text[start:end])
        required = ["name", "link", "summary", "price_type", "category", "why_best"]
        for field in required:
            if field not in tool:
                raise ValueError(f"Missing field: {field}")

        if is_duplicate(tool["link"]):
            logger.info("Best tool is duplicate, falling back to fetch_all_tools")
            all_tools = await fetch_all_tools()
            if all_tools:
                return all_tools[0]
            return _fallback_tool()

        return tool

    except Exception as e:
        logger.error(f"Error fetching best tool via OpenRouter: {e}")
        return _fallback_tool()


def _fallback_tool():
    return {
        "name": "TheresAnAIForThat",
        "link": "https://theresanaiforthat.com",
        "summary": "Best directory for latest AI tools",
        "price_type": "Free",
        "category": "Directory",
        "why_best": "Largest AI tools collection updated daily",
    }
