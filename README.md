# 🤖 AI Drop Daily Bot

A fully automated Telegram bot that finds, analyzes, and posts the latest AI tools to your channel — twice every day.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-@Ai_Drop_Daily-2CA5E0?logo=telegram&logoColor=white)](https://t.me/Ai_Drop_Daily)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-6366f1?logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📺 Live Channel → [@Ai_Drop_Daily](https://t.me/Ai_Drop_Daily)

---

## ✨ Features

- 🔍 Fetches latest AI tools daily using OpenRouter AI
- 🧠 Analyzes each tool — description, price, score, category
- 🖼️ Generates a clean 1920×1080 banner image automatically
- 📤 Posts to Telegram with rich caption
- 🔔 Sends owner DM after every post (success or failure)
- 🗃️ SQLite database to prevent duplicate posts

---

## 📁 Project Structure

```
Ai_Drop_Daily/
├── main.py            # Entry point
├── scheduler.py       # Morning & evening job scheduling
├── fetcher.py         # Fetches AI tools via OpenRouter
├── gemini_helper.py   # Analyzes & scores each tool
├── image_maker.py     # Generates banner images (Pillow)
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
| `/status` | View current schedule & tool counts |
| `/setpost 09:00 18:00 5 2` | Change post times & tool counts live — no restart needed |
| `/testnow` | Post one tool immediately for testing |
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
GEMINI_IMAGE_API_KEY=your_key
```

**3. Run**
```bash
python main.py
```

---

## ☁️ Deploy on Railway

1. Push repo to GitHub
2. New Project → Deploy from GitHub
3. Add environment variables in Railway dashboard
4. Start command: `python main.py`
5. Deploy ✅

---

## ⚙️ Customize

| Setting | File |
|--------|------|
| Post times & tool counts | `settings.py` |
| Change times live | `/setpost` command on Telegram |
| Banner design | `image_maker.py` |
| Caption format | `poster.py` |
| AI model | `OPENROUTER_MODEL` env variable |

---

## 📄 License

MIT — free to use and modify.

---

> Follow [@Ai_Drop_Daily](https://t.me/Ai_Drop_Daily) for daily AI tool drops! 🚀
