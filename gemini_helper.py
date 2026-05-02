"""
gemini_helper.py
Analyzes AI tools using OpenRouter API (OpenAI-compatible).
"""
import requests
import json
import logging
import time
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

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


def analyze_tool(tool_name, tool_summary, tool_link):
    """Analyze an AI tool and return structured info dict."""
    default = {
        "short_description": "AI tool for various tasks",
        "use_case": "Anyone looking for AI solutions",
        "price_type": "Free",
        "score": 5,
        "emoji": "🤖",
        "category": "Other",
    }

    try:
        prompt = f"""Analyze this AI tool and return a JSON object with these keys:
- short_description: max 2 lines explaining what the tool does (English only)
- use_case: one line who should use this (English only)
- price_type: exactly one of: Free, Paid (use Free if it has a free tier)
- score: integer 1-10 based on usefulness and innovation
- emoji: one relevant emoji
- category: one of: Image Generation, Writing, Coding, Video, Audio, Productivity, Research, Other

Tool Name: {tool_name}
Tool Summary: {tool_summary}
Tool Link: {tool_link}

Return ONLY the JSON object, no markdown, no extra text."""

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3,
        }

        response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()

        time.sleep(2)

        start = text.find("{")
        end   = text.rfind("}") + 1
        if start == -1 or end == 0:
            logger.warning(f"No JSON in analyze_tool response: {text[:200]}")
            return default

        result = json.loads(text[start:end])
        required = ["short_description", "use_case", "price_type", "score", "emoji", "category"]

        if not all(k in result for k in required):
            logger.warning(f"Missing keys in analyze_tool response: {result}")
            return default

        if result["price_type"] not in ["Free", "Paid"]:
            result["price_type"] = "Free"
        result["score"] = max(1, min(10, int(result["score"])))
        if not result.get("category"):
            result["category"] = "Other"

        return result

    except Exception as e:
        logger.error(f"Error in analyze_tool for {tool_name}: {e}")
        return default
