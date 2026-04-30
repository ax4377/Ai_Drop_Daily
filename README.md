# AI Drop Daily Bot

A Telegram bot that automatically fetches newly launched AI tools and posts them to a Telegram channel twice daily at 9 AM and 6 PM IST.

## Features

- Fetches AI tools from Product Hunt, TheresAnAIForThat, and Hugging Face Blog RSS feeds
- Uses Gemini AI to analyze and score each tool
- Creates attractive image cards for each tool
- Posts to Telegram channel with formatted captions
- Avoids duplicate posts using SQLite database
- Scheduled posting: 5 tools at 9 AM IST, 2 top-scored tools at 6 PM IST
- Railway deployment ready with environment variable configuration
- Comprehensive error handling and logging

## Project Structure

```
ai-drop-daily-bot/
├── main.py              # Entry point
├── scheduler.py         # APScheduler configuration
├── fetcher.py           # RSS feed fetching
├── gemini_helper.py     # Gemini AI analysis
├── image_maker.py       # Image generation with Pillow
├── poster.py            # Telegram posting logic
├── database.py          # SQLite database operations
├── config.py            # Configuration from environment variables
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Setup Instructions

### 1. Get Telegram Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow the instructions to create a new bot
3. BotFather will give you a token like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
4. Save this token for later use

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" and create a new API key
4. Save this key for later use

### 3. Set Up Telegram Channel

1. Create a new Telegram channel (or use an existing one)
2. Set the channel username to `@Ai_Drop_Daily` (without the @ symbol when creating)
3. Add your bot as an administrator to the channel:
   - Go to Channel Settings → Administrators → Add Administrator
   - Search for your bot by username and add it
   - Make sure the bot has permission to post messages

### 4. Install Dependencies

```bash
# Clone the repository
git clone <your-repository-url>
cd ai-drop-daily-bot

# Install Python dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Run the Bot Locally

```bash
python main.py
```

You should see logs indicating the bot has started and the scheduler is running.

### 7. Deploy to Railway

1. Create a [Railway](https://railway.app/) account
2. Click "New Project" → "Deploy from GitHub" (or upload directly)
3. Select your repository
4. Railway will automatically detect the `requirements.txt` and install dependencies
5. Add the environment variables in Railway dashboard:
   - Go to your project → Variables
   - Add `TELEGRAM_BOT_TOKEN` and `GEMINI_API_KEY` with your values
6. Set the start command to: `python main.py`
7. Deploy the project

### 8. Verify Deployment

Once deployed, the bot should:
- Start successfully and log "AI Drop Daily Bot Started Successfully"
- Initialize the database
- Start the scheduler
- Post the first set of tools at the next scheduled time (9 AM or 6 PM IST)

## How It Works

1. **Scheduler**: Uses APScheduler to run jobs at 9 AM and 6 PM IST daily
2. **Fetcher**: Retrieves new AI tools from RSS feeds using feedparser
3. **Analyzer**: Uses Gemini AI to analyze each tool and generate descriptions, use cases, price types, scores, and emojis
4. **Image Creator**: Generates 1080x1080 pixel image cards using Pillow with:
   - Dark background with gradient effect
   - Cyan top border
   - Tool name and emoji
   - Short description
   - Price badge (green for Free, yellow for Freemium, red for Paid)
   - Score display
   - Watermark
5. **Poster**: Sends images to Telegram channel with formatted captions
6. **Database**: SQLite database tracks posted tools to prevent duplicates

## Error Handling

- Each module has comprehensive try-except blocks
- If one RSS feed fails, others continue to work
- If Gemini API fails, default values are used
- If image creation fails, a basic fallback image is generated
- If posting to Telegram fails for one tool, others continue to be posted
- The bot continues running even if individual steps fail

## Customization

- Adjust posting times in `scheduler.py`
- Change the number of tools posted in `config.py` (MORNING_MAX_TOOLS, EVENING_MAX_TOOLS)
- Modify the image design in `image_maker.py`
- Change the caption format in `poster.py`
- Add more RSS feeds in `fetcher.py`

## License

MIT License - feel free to use and modify this bot for your own AI tool sharing needs!

## Support

If you encounter any issues or have questions, please open an issue in the repository.