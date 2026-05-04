"""
fetcher.py
Google Sheets se aaj ke AI tools fetch karo.
OpenRouter sirf Telegram caption format karne ke liye use hoga.
"""
import requests
import logging
from datetime import datetime, timezone, timedelta
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, GOOGLE_SHEET_ID, GOOGLE_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://t.me/Ai_Drop_Daily",
    "X-Title": "AI Drop Daily Bot",
}


def _get_today_ist():
    """Aaj ki date IST mein return karo (YYYY-MM-DD format)."""
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%Y-%m-%d")


def _fetch_sheet_rows():
    """
    Google Sheets API se saari rows fetch karo.
    Sheet structure: Column A = Date, Column B = Tools Info
    Public sheet — API key se access hoga.
    """
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}"
        f"/values/A:B?key={GOOGLE_API_KEY}"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        rows = data.get("values", [])
        logger.info(f"Sheet se {len(rows)} rows mili")
        return rows
    except Exception as e:
        logger.error(f"Google Sheets fetch error: {e}")
        return []


def _parse_sheet_date(date_str: str) -> str:
    """
    Sheet ki date ko YYYY-MM-DD format mein convert karo.
    Support: ISO format (2026-04-19T13:18:01+00:00) aur plain (2026-04-19)
    """
    if not date_str:
        return ""
    try:
        date_part = date_str.strip().split("T")[0]
        datetime.strptime(date_part, "%Y-%m-%d")
        return date_part
    except Exception:
        return date_str.strip()


def _get_todays_tools_from_sheet():
    """
    Sheet se aaj ki date wale tools filter karo.
    Returns: list of raw tool text strings
    """
    today = _get_today_ist()
    logger.info(f"Aaj ki date (IST): {today}")

    rows = _fetch_sheet_rows()
    if not rows:
        return []

    # Row 1 header skip karo
    tools_today = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        date_cell = _parse_sheet_date(row[0])
        tool_text = row[1].strip() if row[1] else ""

        if date_cell == today and tool_text:
            tools_today.append(tool_text)

    logger.info(f"Aaj ke {len(tools_today)} tools mile sheet mein")
    return tools_today


def _format_caption_via_openrouter(raw_text: str) -> str:
    """
    OpenRouter se raw tool text ko clean Telegram caption mein convert karo.
    Sirf formatting — jo sheet mein hai wohi use hoga, kuch invent nahi hoga.
    """
    prompt = f"""You are a Telegram channel formatter for an AI tools channel called "AI Drop Daily".

Convert the following raw AI tool description into a clean, engaging Telegram post caption.

Rules:
- Start with a relevant emoji + tool name in bold (use *bold* markdown)
- Write 2-3 clean lines about what the tool does (use the info given, do not invent)
- If a link/repo is mentioned in the text, include it as: 🔗 <link>
- End with relevant hashtags: #AI #AITools #AIDrop
- Keep total length under 280 characters (excluding hashtags)
- Do NOT add any info that is not in the original text
- Output ONLY the caption, nothing else

Raw text:
{raw_text}"""

    try:
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.5,
        }
        response = requests.post(
            OPENROUTER_URL, headers=OPENROUTER_HEADERS, json=payload, timeout=60
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices")
        if not choices:
            logger.error(f"OpenRouter no choices: {data}")
            return raw_text

        caption = choices[0].get("message", {}).get("content", "").strip()
        if not caption:
            return raw_text

        return caption

    except Exception as e:
        logger.error(f"OpenRouter caption format error: {e}")
        return raw_text  # Fallback — raw text as-is


async def fetch_all_tools():
    """
    Main function — scheduler.py ye call karta hai.
    Google Sheet se aaj ke tools lao, OpenRouter se format karo.
    Returns: list of dicts with 'caption' key ready for posting.
    """
    raw_tools = _get_todays_tools_from_sheet()

    if not raw_tools:
        logger.warning("Aaj ke liye sheet mein koi tools nahi mile.")
        return []

    formatted_tools = []
    for i, raw_text in enumerate(raw_tools):
        logger.info(f"Formatting tool {i+1}/{len(raw_tools)}...")
        caption = _format_caption_via_openrouter(raw_text)
        formatted_tools.append({
            "caption": caption,
            "raw": raw_text,
        })

    logger.info(f"Total {len(formatted_tools)} tools formatted aur ready")
    return formatted_tools
