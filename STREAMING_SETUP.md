# Streaming Setup Guide

## Issue: Stream Error

The streaming error occurs because **STREAMING_BOT_USERNAME** is not configured in your environment.

## What You Need

To enable streaming, you need a **Telegram File Streaming Bot** that converts Telegram files into HTTP streaming URLs.

## Recommended Streaming Bots

### Option 1: TG File Stream Bot (Recommended)
- Bot: `@TG_FileStreamBot`
- Features: Converts Telegram files to streamable HTTP links
- Setup: Start the bot and forward any file to get a stream link

### Option 2: Deploy Your Own
- Use: https://github.com/EverythingSuckz/TG-FileStreamBot
- Deploy on Heroku, Railway, or your own server
- Full control over streaming infrastructure

### Option 3: Other Public Bots
- `@FileToLinkBot`
- `@GetPublicLinkBot`
- Search for "Telegram file to link bot"

## Configuration Steps

### 1. Create `.env` file

Create a file named `.env` in the `BBHC-Theatre` directory:

```env
# Telegram API Credentials
API_ID=26840260
API_HASH=b38ca5e47129f33da3b4d2dcb5700aa0

# Search Bot
SEARCH_BOT_USERNAME=TheProSearchBot

# Streaming Bot (REQUIRED for streaming)
STREAMING_BOT_USERNAME=TG_FileStreamBot

# Optional: Your own streaming bot token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Domain for streaming (if using your own bot)
DOMAIN=http://localhost:8000
```

### 2. Test the Streaming Bot

1. Open Telegram and search for your chosen streaming bot (e.g., `@TG_FileStreamBot`)
2. Start the bot with `/start`
3. Forward any video file to the bot
4. Check if it returns a streaming URL
5. If yes, use that bot's username in your `.env` file

### 3. Restart the Backend

After creating the `.env` file:

```bash
# Stop the current backend (Ctrl+C)
# Then restart:
cd backend
python main.py
```

## Alternative: Download Instead of Stream

If you don't want to set up streaming, you can use the **Download** button instead:
- Click on a movie
- Click the "Download" button (instead of "Stream")
- The file will be downloaded to your computer
- Play it with your local media player

## Temporary Workaround

While setting up streaming, you can modify the frontend to show a helpful error message:

The system will now show: "Streaming bot not configured. Please set STREAMING_BOT_USERNAME in .env file."

## Need Help?

1. **Check if bot is working**: Send a file to the bot manually
2. **Verify .env file**: Make sure it's in the correct directory
3. **Check bot username**: Should not include @ symbol in .env
4. **Restart backend**: Changes require a restart

## Example Working Configuration

```env
API_ID=26840260
API_HASH=b38ca5e47129f33da3b4d2dcb5700aa0
SEARCH_BOT_USERNAME=TheProSearchBot
STREAMING_BOT_USERNAME=TG_FileStreamBot
```

Save this as `.env` in the `BBHC-Theatre` folder, then restart the backend.
