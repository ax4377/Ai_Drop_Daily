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
        "short_description": f"{tool_name} is an AI-powered tool designed to help with various tasks efficiently.",
        "use_case": "Professionals and creators looking for AI-powered solutions",
        "price_type": "Free",
        "score": 5,
        "emoji": "🤖",
        "category": "Other",
    }

    try:
        # Fix 1: Prompt me clearly bola gaya hai ki "..." ya placeholder mat dena
        prompt = f"""You are an AI tools analyst. Analyze the tool below and return a JSON object.

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

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,   # Fix 2: 500 → 600 taaki response cut na ho
            "temperature": 0.3,
        }

        response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()

        # Fix 3: Reasoning model ke liye content + reasoning dono check karo
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            logger.warning(f"No choices in analyze_tool response for {tool_name}")
            return default

        message = choices[0].get("message", {})
        text = message.get("content")

        # Reasoning model fallback
        if text is None:
            text = message.get("reasoning", "")
            if text:
                logger.warning(f"analyze_tool: using reasoning field for {tool_name}")

        if not text or not text.strip():
            logger.warning(f"Empty response in analyze_tool for {tool_name}")
            return default

        text = text.strip()
        time.sleep(2)

        # JSON extract karo
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start == -1 or end == 0:
            logger.warning(f"No JSON in analyze_tool response for {tool_name}: {text[:200]}")
            return default

        result = json.loads(text[start:end])
        required = ["short_description", "use_case", "price_type", "score", "emoji", "category"]

        if not all(k in result for k in required):
            logger.warning(f"Missing keys in analyze_tool for {tool_name}: {result}")
            return default

        # Fix 4: "..." ya empty values ko default se replace karo
        if not result.get("short_description") or result["short_description"].strip() in ["...", ".", ""]:
            logger.warning(f"short_description is placeholder for {tool_name}, using default")
            result["short_description"] = default["short_description"]

        if not result.get("use_case") or result["use_case"].strip() in ["...", ".", ""]:
            logger.warning(f"use_case is placeholder for {tool_name}, using default")
            result["use_case"] = default["use_case"]

        # Validations
        if result["price_type"] not in ["Free", "Paid"]:
            result["price_type"] = "Free"
        result["score"] = max(1, min(10, int(result["score"])))
        if not result.get("category"):
            result["category"] = "Other"
        if not result.get("emoji"):
            result["emoji"] = "🤖"

        logger.info(f"analyze_tool success for {tool_name}: score={result['score']}, price={result['price_type']}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in analyze_tool for {tool_name}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error in analyze_tool for {tool_name}: {e}")
        return default
