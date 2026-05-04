"""
fetcher.py
Google Sheets se aaj ke raw AI tool text fetch karo.
OpenRouter se name, link, summary, price_type, category extract karo.
poster.py + gemini_helper.py baki kaam karenge — purana format same rahega.
"""
import requests
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, GOOGLE_SHEET_ID, GOOGLE_API_KEY
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


def _get_today_ist():
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%Y-%m-%d")


def _fetch_sheet_rows():
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}"
        f"/values/A:B?key={GOOGLE_API_KEY}"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        rows = response.json().get("values", [])
        logger.info(f"Sheet se {len(rows)} rows mili")
        return rows
    except Exception as e:
        logger.error(f"Google Sheets fetch error: {e}")
        return []


def _parse_sheet_date(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        date_part = date_str.strip().split("T")[0]
        datetime.strptime(date_part, "%Y-%m-%d")
        return date_part
    except Exception:
        return date_str.strip()


def _get_todays_raw_tools():
    today = _get_today_ist()
    logger.info(f"Aaj ki date (IST): {today}")
    rows = _fetch_sheet_rows()
    if not rows:
        return []
    tools_today = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        if _parse_sheet_date(row[0]) == today and row[1].strip():
            tools_today.append(row[1].strip())
    logger.info(f"Aaj ke {len(tools_today)} raw tools mile sheet mein")
    return tools_today


def _extract_tool_fields(raw_text: str) -> dict:
    """
    OpenRouter se raw text ko parse karke structured fields nikalo.
    name, link, summary, price_type, category — poster.py ko ye chahiye.
    """
    default = {
        "name": "AI Tool",
        "link": "https://theresanaiforthat.com",
        "summary": raw_text[:200],
        "price_type": "Free",
        "category": "Other",
    }

    prompt = f"""Extract structured information from this AI tool description.

Raw text:
{raw_text}

Return ONLY a valid JSON object with exactly these keys:
{{
  "name": "SHORT tool brand name only — max 3 words, no descriptions (e.g. 'Runway Gen-2', 'Claude Code', 'Higgsfield MCP')",
  "link": "working URL starting with https:// — extract from text or infer from tool name (string)",
  "summary": "2 clear sentences about what the tool does (string)",
  "price_type": "Free or Freemium or Paid (string)",
  "category": "one of: Image Generation, Writing, Coding, Video, Audio, Productivity, Research, Other (string)"
}}

Rules:
- "name" must be the SHORT brand/product name only — NOT a description. Examples: good: "Seedance 2.0", "GPT Image 2", "GRWM AI" — bad: "GRWM AI video using GPT Image 2 + Seedance 2.0"
- Extract the link/URL from the text if present, otherwise use the official website
- summary must be clear and informative
- Return ONLY the JSON object, nothing else"""

    try:
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.3,
        }
        response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        choices = data.get("choices")
        if not choices:
            logger.error(f"OpenRouter no choices: {data}")
            return default

        text = choices[0].get("message", {}).get("content", "").strip()
        if not text:
            return default

        # JSON extract karo
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            logger.warning(f"No JSON found in extract response: {text[:200]}")
            return default

        result = json.loads(text[start:end])

        # Validate required fields
        for field in ["name", "link", "summary", "price_type", "category"]:
            if not result.get(field):
                result[field] = default[field]

        if not result["link"].startswith("http"):
            result["link"] = default["link"]

        if result["price_type"] not in ["Free", "Freemium", "Paid"]:
            result["price_type"] = "Free"

        logger.info(f"Extracted tool: {result['name']} | {result['link']}")
        return result

    except Exception as e:
        logger.error(f"Error extracting tool fields: {e}")
        return default


async def fetch_all_tools() -> list:
    """
    Main function — scheduler.py ye call karta hai.
    Google Sheet se raw text lao → OpenRouter se fields nikalo → list return karo.
    poster.py + gemini_helper.py same purane format mein kaam karenge.
    """
    raw_tools = _get_todays_raw_tools()

    if not raw_tools:
        logger.warning("Aaj ke liye sheet mein koi tools nahi mile.")
        return []

    structured_tools = []
    for i, raw_text in enumerate(raw_tools):
        logger.info(f"Extracting fields for tool {i+1}/{len(raw_tools)}...")
        tool = _extract_tool_fields(raw_text)

        # Duplicate check
        if is_duplicate(tool["link"]):
            logger.info(f"Duplicate skip: {tool['link']}")
            continue

        structured_tools.append(tool)

    logger.info(f"Total {len(structured_tools)} tools ready for posting")
    return structured_tools
