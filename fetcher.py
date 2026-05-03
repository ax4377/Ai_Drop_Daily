"""
fetcher.py
Fetches trending AI tools using OpenRouter API (OpenAI-compatible).
Reasoning models support included — content None hone par reasoning field use hota hai.
"""
import requests
import json
import logging
import re
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


def _call_openrouter(prompt: str, max_tokens: int = 8000) -> str:
    """
    OpenRouter ko prompt bhejo aur text return karo.
    Reasoning models ke liye content + reasoning dono check karta hai.
    max_tokens 8000 — reasoning models zyada tokens use karte hain thinking mein.
    """
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=90)
    response.raise_for_status()

    data = response.json()
    choices = data.get("choices")
    if not choices:
        logger.error(f"No choices in response: {data}")
        raise ValueError("No choices in OpenRouter response")

    message      = choices[0].get("message", {})
    finish_reason = choices[0].get("finish_reason", "unknown")
    text          = message.get("content")

    # Reasoning model fallback — content None hota hai, reasoning mein actual response hota hai
    if not text:
        reasoning = message.get("reasoning", "")
        if reasoning:
            logger.info(f"Reasoning model detected — extracting from reasoning field (finish_reason={finish_reason})")
            text = reasoning
        else:
            logger.error(f"Both content and reasoning empty. finish_reason={finish_reason}")
            raise ValueError(f"Empty response. finish_reason={finish_reason}")

    return text.strip()


def _extract_json_array(text: str):
    """
    Text se JSON array extract karo.
    Reasoning models aksar bohot zyada text ke beech mein JSON daalte hain —
    isliye last valid JSON array dhundho (reasoning ke baad actual answer hota hai).
    """
    # Sabse pehle markdown code blocks hata do
    text = re.sub(r'```(?:json)?', '', text)

    # Saare [ ... ] blocks dhundo
    candidates = []
    depth = 0
    start_idx = None

    for i, ch in enumerate(text):
        if ch == '[':
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0 and start_idx is not None:
                candidates.append(text[start_idx:i+1])
                start_idx = None

    if not candidates:
        logger.warning(f"No JSON array brackets found in text (len={len(text)})")
        return None

    # Last candidate prefer karo — reasoning models mein actual answer end mein hota hai
    for candidate in reversed(candidates):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list) and len(parsed) > 0:
                logger.info(f"JSON array extracted: {len(parsed)} items")
                return parsed
        except json.JSONDecodeError:
            continue

    logger.warning("No valid JSON array found in any candidate")
    return None


def validate_tools_list(tools):
    """Tools list validate karo — incomplete entries hata do."""
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

        # Reasoning models ke liye prompt aur clear example diya hai
        prompt = """You are an AI tools researcher. List 15 recently launched or trending AI tools from 2025-2026.

Your final answer must be ONLY a valid JSON array — nothing else after the array.

Each object must have exactly these 5 keys:
  "name"       - tool name (string)
  "link"       - real working URL starting with https:// (string)
  "summary"    - 2 sentences about what the tool does (string)
  "price_type" - exactly one of: Free, Freemium, Paid (string)
  "category"   - one of: Image Generation, Writing, Coding, Video, Audio, Productivity, Research, Other (string)

Example format:
[
  {
    "name": "Midjourney",
    "link": "https://midjourney.com",
    "summary": "AI image generation tool that creates stunning visuals from text prompts. Supports multiple art styles and high-resolution outputs.",
    "price_type": "Paid",
    "category": "Image Generation"
  }
]

Return exactly 15 tools. Output the JSON array as your final answer."""

        text = _call_openrouter(prompt)
        time.sleep(1)

        tools = _extract_json_array(text)
        if tools is None:
            logger.warning(f"Could not extract JSON array. Text preview: {text[-500:]}")
            return []

        tools = validate_tools_list(tools)
        new_tools = [t for t in tools if not is_duplicate(t["link"])]
        logger.info(f"{len(new_tools)} new tools after duplicate filter")

        if len(new_tools) < 3:
            logger.warning(f"Only {len(new_tools)} new tools — may need to clear database")

        return new_tools

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in fetch_all_tools: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching tools via OpenRouter: {e}")
        return []


async def fetch_best_tool():
    """Fetch the single most impressive AI tool via OpenRouter."""
    try:
        logger.info(f"Fetching best AI tool via OpenRouter ({MODEL})...")

        prompt = """You are an AI tools researcher. What is the single most impressive AI tool launched in 2025-2026?

Your final answer must be ONLY a valid JSON object — nothing else after the object.

Required keys:
  "name"       - tool name (string)
  "link"       - real working URL starting with https:// (string)
  "summary"    - 3 sentences about the tool (string)
  "price_type" - exactly one of: Free, Freemium, Paid (string)
  "category"   - one of: Image Generation, Writing, Coding, Video, Audio, Productivity, Research, Other (string)
  "why_best"   - 1 sentence why it stands out (string)

Output the JSON object as your final answer."""

        text = _call_openrouter(prompt)
        time.sleep(1)

        # Last { ... } extract karo
        text_clean = re.sub(r'```(?:json)?', '', text)
        # Find last valid JSON object
        last_obj = None
        depth = 0
        start_idx = None
        for i, ch in enumerate(text_clean):
            if ch == '{':
                if depth == 0:
                    start_idx = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    try:
                        candidate = json.loads(text_clean[start_idx:i+1])
                        if isinstance(candidate, dict):
                            last_obj = candidate
                    except:
                        pass
                    start_idx = None

        if not last_obj:
            raise ValueError("No valid JSON object found")

        required = ["name", "link", "summary", "price_type", "category", "why_best"]
        for field in required:
            if field not in last_obj:
                raise ValueError(f"Missing field: {field}")

        if is_duplicate(last_obj["link"]):
            logger.info("Best tool is duplicate, falling back to fetch_all_tools")
            all_tools = await fetch_all_tools()
            if all_tools:
                return all_tools[0]
            return _fallback_tool()

        return last_obj

    except Exception as e:
        logger.error(f"Error fetching best tool via OpenRouter: {e}")
        return _fallback_tool()


def _fallback_tool():
    return {
        "name": "TheresAnAIForThat",
        "link": "https://theresanaiforthat.com",
        "summary": "The largest directory of AI tools updated daily. Helps you find the right AI for any task.",
        "price_type": "Free",
        "category": "Research",
        "why_best": "Largest AI tools collection updated daily",
    }



