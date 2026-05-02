# 🤖 AI Drop Daily Bot

> A fully automated Telegram bot that discovers, analyzes, and posts the latest AI tools to your channel — twice every day. No manual work needed.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram&logoColor=white)](https://t.me/Ai_Drop_Daily)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-6366f1?logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📺 Live Channel

👉 **[@Ai_Drop_Daily](https://t.me/Ai_Drop_Daily)** — Follow to get fresh AI tools every day at **9 AM** and **6 PM IST**

---

## ✨ What It Does

Every day the bot automatically:

1. **Fetches** the newest AI tools using OpenRouter AI (supports Gemini 2.5, GPT-4o, and 200+ models)
2. **Analyzes** each tool — generates description, use case, category, pricing, and a quality score
3. **Designs** a beautiful 1920×1080 banner image using Pillow (no external design APIs needed)
4. **Posts** to Telegram with a rich caption — emoji, description, use case, price, score, and link
5. **Notifies** the owner on Telegram DM after every post (success or failure)
6. **Tracks** every posted tool in SQLite to avoid duplicate posts forever

---

## 🗂️ Project Structure

```
Ai_Drop_Daily/
├── main.py              # Entry point — starts bot + scheduler
├── scheduler.py         # APScheduler — morning & evening jobs
├── fetcher.py           # OpenRouter AI — fetches & discovers new tools
├── gemini_helper.py     # OpenRouter AI — analyzes & scores each tool
├── image_maker.py       # Pillow — generates 1920×1080 banner images
├── poster.py            # Telegram — sends image + caption to channel
├── database.py          # SQLite — duplicate detection & post history
├── bot_commands.py      # Telegram commands — /setpost, /status, etc.
├── config.py            # Environment variable loader
├── settings.py          # Default posting schedule & tool limits
├── requirements.txt     # Python dependencies
├── fonts/
│   ├── Poppins-Bold.ttf
│   └── Poppins-Regular.ttf
└── README.md
```

---

## ⚙️ How It Works

```
Scheduler (9 AM / 6 PM IST)
        │
        ▼
  fetcher.py  ──── OpenRouter AI ────▶ Discovers latest AI tools
        │
        ▼
  gemini_helper.py ── Analyzes each tool (score, price, description, emoji)
        │
        ▼
  image_maker.py ──── Generates 1920×1080 banner with Pillow
        │
        ▼
  poster.py ──────── Posts image + caption to @Ai_Drop_Daily
        │
        ├──▶ Owner DM: "✅ Post done! X tools posted."
        │
        ▼
  database.py ────── Saves tool to SQLite (prevents future duplicates)
```

**Morning post (9 AM IST):** Fetches & posts up to 5 new AI tools  
**Evening post (6 PM IST):** Fetches, scores all tools, posts top 2 highest-scored tools

> **Smart caching:** Evening job analyzes tools once for scoring, and `poster.py` reuses that cached result — no double API calls.

---

## 🤖 Bot Commands

All commands are **owner-only** — only the bot owner's Telegram ID can use them. Changes apply **instantly without any restart.**

---

### `/start`
Shows the welcome message and a quick list of all available commands.

---

### `/status`
Shows the current posting schedule and tool limits.

**Example response:**
```
⏰ Current Schedule:

🌅 Post 1: 09:00 IST → 5 tools
🌆 Post 2: 18:00 IST → 2 tools

🟢 Bot is running!
```

---

### `/setpost HH:MM HH:MM max1 max2`

Change posting times and tool counts **live** — no server restart needed.

**Format:**
```
/setpost <Post1 Time> <Post2 Time> <Post1 Max Tools> <Post2 Max Tools>
```

**Examples:**
```
/setpost 09:00 18:00 5 2    → Post 1 at 9 AM (5 tools), Post 2 at 6 PM (2 tools)
/setpost 08:30 15:00 3 1    → Post 1 at 8:30 AM (3 tools), Post 2 at 3 PM (1 tool)
/setpost 10:00 20:00 2 2    → Post 1 at 10 AM (2 tools), Post 2 at 8 PM (2 tools)
```

**Rules:**
- Time must be in **24-hour HH:MM format** (IST timezone)
- Max tools per post must be between **1 and 10**
- Old scheduled jobs are removed and new ones created instantly — no restart needed

**Example response:**
```
✅ Settings updated instantly!

🌅 Post 1: 09:30 IST → 3 tools
🌆 Post 2: 15:00 IST → 2 tools

⚡ No restart needed!
```

---

### `/testnow`

Triggers a post immediately — fetches 1 AI tool and posts it to the channel right now. Useful for testing after deployment.

**Example response:**
```
🔄 Posting test now...
✅ Test post done! Check @Ai_Drop_Daily
```

---

### `/help`
Shows the full command reference with format and examples.

---

## 🚀 Setup & Deployment

### Prerequisites

- Python 3.10+
- A Telegram Bot Token → from [@BotFather](https://t.me/BotFather)
- An OpenRouter API Key → from [openrouter.ai](https://openrouter.ai)
- A Gemini API Key → from [aistudio.google.com](https://aistudio.google.com)

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Ai_Drop_Daily.git
cd Ai_Drop_Daily
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_IMAGE_API_KEY=your_gemini_api_key_here

# Optional — change the AI model (default: google/gemini-2.5-flash)
OPENROUTER_MODEL=google/gemini-2.5-flash
```

### 4. Set Your Owner ID

Open `bot_commands.py` and `scheduler.py`, find this line and replace with your Telegram user ID:

```python
OWNER_ID = 123456789  # Get your ID from @userinfobot on Telegram
```

### 5. Add Bot to Telegram Channel

1. Create a Telegram channel (e.g. `@Ai_Drop_Daily`)
2. Go to **Channel Settings → Administrators → Add Administrator**
3. Search for your bot and add it with **"Post Messages"** permission

### 6. Run Locally

```bash
python main.py
```

You should see:
```
Webhook cleared, pending updates dropped.
Morning job scheduled: 09:00 IST
Evening job scheduled: 18:00 IST
AI Drop Daily Bot Started Successfully
Bot is now running and listening for commands...
```

---

## ☁️ Deploy to Railway (Recommended)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
3. Select this repository
4. Add environment variables in **Railway → Variables**:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENROUTER_API_KEY`
   - `GEMINI_IMAGE_API_KEY`
   - `OPENROUTER_MODEL` *(optional)*
5. Set start command: `python main.py`
6. Click **Deploy** ✅

Railway auto-detects `requirements.txt` and installs everything. The bot stays running 24/7.

After deployment, send `/testnow` to your bot on Telegram to verify it works.

---

## 🛠️ Customization

| What to change | Where |
|----------------|-------|
| Default posting times | `settings.py` → `FIRST_POST_TIME_HOUR`, `SECOND_POST_TIME_HOUR` |
| Default tool counts | `settings.py` → `FIRST_MAX_TOOLS`, `SECOND_MAX_TOOLS` |
| Posting times at runtime | `/setpost` command via Telegram (no restart needed) |
| AI model used | `OPENROUTER_MODEL` env variable |
| Banner design (colors, fonts, spacing) | `image_maker.py` |
| Caption format | `poster.py` |
| Channel username | `settings.py` → `CHANNEL_ID` |
| Delay between posts | `settings.py` → `POST_DELAY_SECONDS` |
| Watermark text on banner | `image_maker.py` → `watermark` parameter in `create_tool_card()` |

---

## 📦 Dependencies

```
python-telegram-bot[job-queue]==21.5
google-genai
Pillow
APScheduler==3.10.4
pytz
requests
python-dotenv
```

---

## 🔒 Error Handling

The bot is built to keep running even when individual steps fail:

| Failure | What happens |
|---------|-------------|
| OpenRouter API fails | Default values used for that tool |
| One tool's image fails | That tool is skipped, others continue |
| Telegram post fails | Error logged, next tool continues |
| Duplicate tool detected | Silently skipped via SQLite check |
| Any job fails | Owner gets a Telegram DM: `❌ Post failed! Error: ...` |

---

## 📄 License

MIT License — free to use, modify, and deploy for your own AI channel.

---

## 🙌 Support

If you find this project useful, **follow [@Ai_Drop_Daily](https://t.me/Ai_Drop_Daily)** on Telegram for daily AI tool drops!

For bugs or questions, open an [Issue](https://github.com/your-username/Ai_Drop_Daily/issues) on GitHub.
