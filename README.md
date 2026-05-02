# 🤖 AI Drop Daily Bot

> A fully automated Telegram bot that discovers, analyzes, and posts the latest AI tools to your channel — twice every day.

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

1. **Fetches** the newest AI tools using OpenRouter AI (supports GPT-4o, Gemini 2.5, and more)
2. **Analyzes** each tool — generates description, use case, category, pricing, and a quality score
3. **Designs** a beautiful 16:9 banner image using Pillow (no external design APIs needed)
4. **Posts** to Telegram with a rich caption — price badge, score, use case, and tool link
5. **Tracks** every posted tool in SQLite to avoid duplicate posts

---

## 🖼️ Sample Output

The bot generates clean Apple-keynote style banners for each tool:

- **Title** — Tool name in large bold Poppins font
- **Description** — 2-line AI-generated summary
- **Watermark** — `@Ai_Drop_Daily` at the bottom
- Light gray background with subtle grid and soft card shadow

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
├── database.py          # SQLite — duplicate detection & history
├── config.py            # Environment variable loader
├── settings.py          # Posting schedule & limits
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
  fetcher.py  ──── OpenRouter AI ──── Discovers latest AI tools
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
        ▼
  database.py ────── Saves tool name to prevent future duplicates
```

**Morning post (9 AM):** Up to 5 new AI tools  
**Evening post (6 PM):** 2 top-scored tools of the day

---

## 🚀 Setup & Deployment

### Prerequisites

- Python 3.10+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- An OpenRouter API Key (from [openrouter.ai](https://openrouter.ai))
- A Gemini API Key for image generation (from [aistudio.google.com](https://aistudio.google.com))

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

# Optional — change the AI model used (default: google/gemini-2.5-flash)
OPENROUTER_MODEL=google/gemini-2.5-flash
```

### 4. Add Bot to Telegram Channel

1. Create a Telegram channel (e.g. `@Ai_Drop_Daily`)
2. Go to **Channel Settings → Administrators → Add Administrator**
3. Search for your bot and add it with **"Post Messages"** permission

### 5. Run Locally

```bash
python main.py
```

You should see:
```
AI Drop Daily Bot Started Successfully
Bot is now running and listening for commands...
```

---

## ☁️ Deploy to Railway (Recommended)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
3. Select this repository
4. Add your environment variables in **Railway → Variables**:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENROUTER_API_KEY`
   - `GEMINI_IMAGE_API_KEY`
5. Set start command: `python main.py`
6. Deploy ✅

Railway will auto-detect `requirements.txt` and install everything.

---

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/status` | Check bot status and next scheduled post time |
| `/testnow` | Trigger a test post immediately (owner only) |
| `/setpost` | Change posting schedule (owner only) |
| `/help` | Show all available commands |

---

## 🛠️ Customization

| What to change | Where |
|----------------|-------|
| Posting times (9 AM / 6 PM) | `settings.py` |
| Number of tools per post | `settings.py` → `FIRST_MAX_TOOLS`, `SECOND_MAX_TOOLS` |
| AI model used | `OPENROUTER_MODEL` env variable |
| Banner design (colors, fonts, layout) | `image_maker.py` |
| Caption format | `poster.py` |
| Watermark text | `image_maker.py` → `watermark` parameter |

---

## 📦 Dependencies

```
python-telegram-bot[job-queue]==21.5
Pillow
APScheduler==3.10.4
pytz
requests
python-dotenv
google-genai
```

---

## 🔒 Error Handling

The bot is built to keep running even when individual steps fail:

- If OpenRouter API fails → default tool values are used
- If one tool's image fails → next tool continues
- If Telegram post fails → error is logged, bot keeps running
- If duplicate is detected → tool is silently skipped
- All errors are sent to the owner's Telegram DM automatically

---

## 📄 License

MIT License — free to use, modify, and deploy for your own AI channel.

---

## 🙌 Support

If you find this project useful, **follow [@Ai_Drop_Daily](https://t.me/Ai_Drop_Daily)** on Telegram!
