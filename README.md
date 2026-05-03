# 🤖 AI Drop Daily Bot

A fully automated Telegram bot that finds, analyzes, and posts the latest AI tools to your channel — twice every day.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-@Ai_Drop_Daily-2CA5E0?logo=telegram&logoColor=white)](https://t.me/Ai_Drop_Daily)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-6366f1?logo=railway&logoColor=white)](https://railway.app)

---

## 📺 Live Channel → [@Ai_Drop_Daily](https://t.me/Ai_Drop_Daily)

---

## ✨ Features

- 🔍 Fetches real, verified AI tools via OpenRouter
- 🧠 Analyzes each tool — description, price, score, category
- 🖼️ Generates a clean 1920×1080 banner with score badge + price badge
- 📤 Posts to Telegram with rich caption
- 🔔 Sends owner DM after every post (success or failure)
- 🗃️ SQLite database to prevent duplicate posts

---

## 📁 Project Structure

```
Ai_Drop_Daily/
├── main.py            # Entry point
├── scheduler.py       # Morning & evening job scheduling
├── fetcher.py         # Fetches real AI tools via OpenRouter
├── gemini_helper.py   # Analyzes & scores each tool
├── image_maker.py     # Generates banner images (Pillow) with badges
├── poster.py          # Posts to Telegram channel
├── database.py        # Duplicate tracking (SQLite)
├── bot_commands.py    # Telegram bot commands
├── config.py          # Env variable loader
├── settings.py        # Schedule & limits config
├── fonts/             # Poppins Bold & Regular
└── requirements.txt
```

---

## 🤖 Bot Commands

| Command | Description |
|--------|-------------|
| `/start` | Welcome message |
| `/status` | Schedule, today's count, total DB count |
| `/setpost 09:00 18:00 5 2` | Change post times & tool counts live |
| `/testnow` | Post one tool immediately for testing |
| `/listtoday` | Show today's posted tools |
| `/cleardb` | Reset duplicate database (when 0 tools fetch ho) |
| `/help` | Show all commands |

> 🔒 All commands are owner-only.

---

## 🚀 Quick Start

**1. Clone & install**
```bash
git clone https://github.com/your-username/Ai_Drop_Daily.git
cd Ai_Drop_Daily
pip install -r requirements.txt
```

**2. Create `.env` file**
```env
TELEGRAM_BOT_TOKEN=your_token
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=google/gemini-2.5-flash
```

**3. Run**
```bash
python main.py
```

---

## ☁️ Deploy on Railway

1. Push repo to GitHub
2. New Project → Deploy from GitHub
3. Add environment variables in Railway dashboard:

```
TELEGRAM_BOT_TOKEN=your_token
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=google/gemini-2.5-flash

# Optional: Set schedule (restart-proof settings)
MORNING_HOUR=9
MORNING_MINUTE=10
EVENING_HOUR=18
EVENING_MINUTE=10
MORNING_MAX_TOOLS=5
EVENING_MAX_TOOLS=2
```

4. Start command: `python main.py`
5. Deploy ✅

---

## ⚙️ Customize

| Setting | How |
|--------|------|
| Post times & tool counts | Railway Variables (restart-proof) OR `/setpost` command |
| Banner design | `image_maker.py` |
| Caption format | `poster.py` |
| AI model | `OPENROUTER_MODEL` env variable |
| Channel ID | `settings.py` → `CHANNEL_ID` |

---

## 🔧 Persistence (Important for Railway)

Railway destroys the container on every redeploy. To make schedule settings **restart-proof**:

Set these in Railway Variables dashboard:
```
MORNING_HOUR, MORNING_MINUTE
EVENING_HOUR, EVENING_MINUTE  
MORNING_MAX_TOOLS, EVENING_MAX_TOOLS
```

When you use `/setpost`, it saves to `runtime_settings.json` AND shows you the Railway Variables to set.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `409 Conflict` on startup | Normal — bot handles it with retry. Wait 30s. |
| `0 tools fetched` every time | Run `/cleardb` to reset duplicate DB |
| Settings reset after redeploy | Set Railway Variables (see Persistence section) |
| Fake tool names posted | Use a better model: `google/gemini-2.5-flash` |

---

## 📄 License

MIT — free to use and modify.
