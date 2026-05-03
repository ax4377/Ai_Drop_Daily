"""
database.py
SQLite database for duplicate tracking and tool history.

No changes to logic — just added thread safety (SQLite connections
should not be shared across threads/async tasks).
Each function creates its own connection and closes it immediately.
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_NAME = "bot_database.db"


def init_db():
    """Initialize the database and create posted_tools table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posted_tools (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name       TEXT NOT NULL,
                tool_link       TEXT UNIQUE NOT NULL,
                tool_description TEXT,
                price_type      TEXT,
                posted_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
                post_session    TEXT CHECK(post_session IN ('morning', 'evening')),
                gemini_score    INTEGER
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


def is_duplicate(link: str) -> bool:
    """Check if a tool link already exists in the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM posted_tools WHERE tool_link = ?", (link,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"Error checking duplicate for link {link}: {e}")
        return False   # Assume not duplicate on error — don't block new tools


def save_tool(tool_name: str, tool_link: str, tool_description: str,
              price_type: str, post_session: str, gemini_score: int):
    """Save a new tool to the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO posted_tools
                (tool_name, tool_link, tool_description, price_type, post_session, gemini_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tool_name, tool_link, tool_description, price_type, post_session, gemini_score))
        conn.commit()
        conn.close()
        logger.info(f"Tool saved: {tool_name}")
    except Exception as e:
        logger.error(f"Error saving tool {tool_name}: {e}")


def get_todays_tools() -> list:
    """Fetch all tools posted today."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tool_name, tool_link, tool_description, price_type,
                   posted_at, post_session, gemini_score
            FROM posted_tools
            WHERE DATE(posted_at) = DATE('now')
            ORDER BY posted_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error fetching today's tools: {e}")
        return []


def get_total_tools_count() -> int:
    """Total tools ever posted — /status command ke liye."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posted_tools")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Error getting total count: {e}")
        return 0


def clear_all_tools() -> int:
    """Delete all tools from database — /cleardb command ke liye. Returns deleted count."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posted_tools")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM posted_tools")
        conn.commit()
        conn.close()
        logger.info(f"Database cleared: {count} tools removed")
        return count
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return 0
