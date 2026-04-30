import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_NAME = "bot_database.db"

def init_db():
    """Initialize the database and create posted_tools table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posted_tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                tool_link TEXT UNIQUE NOT NULL,
                tool_description TEXT,
                price_type TEXT,
                posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                post_session TEXT CHECK(post_session IN ('morning', 'evening')),
                gemini_score INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def is_duplicate(link):
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
        return False  # Assume not duplicate on error to avoid blocking new tools

def save_tool(tool_name, tool_link, tool_description, price_type, post_session, gemini_score):
    """Save a new tool to the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posted_tools (tool_name, tool_link, tool_description, price_type, post_session, gemini_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tool_name, tool_link, tool_description, price_type, post_session, gemini_score))
        conn.commit()
        conn.close()
        logger.info(f"Tool saved: {tool_name}")
    except Exception as e:
        logger.error(f"Error saving tool {tool_name}: {e}")

def get_todays_tools():
    """Fetch all tools posted today."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM posted_tools 
            WHERE DATE(posted_at) = DATE('now')
            ORDER BY posted_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error fetching today's tools: {e}")
        return []

def get_best_tool_today():
    """Fetch the tool with the highest gemini_score posted today."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM posted_tools 
            WHERE DATE(posted_at) = DATE('now')
            ORDER BY gemini_score DESC, posted_at DESC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        logger.error(f"Error fetching best tool today: {e}")
        return None