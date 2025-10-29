# Integration Guide: Search & Stream System

## Overview

This integrated system combines two powerful components:
1. **search.py** - Movie search bot that finds and forwards videos
2. **telegram_video_streamer.py** - Streaming service that generates public video links

## Architecture

```
User → search.py → TheProSearchBot → Forward Video → Streaming Bot → Generate Link → Stream Video
```

## Features

### Search Component (search.py)
- ✅ Search for movies using TheProSearchBot
- ✅ Interactive button navigation and pagination
- ✅ Automatic file forwarding to streaming bot
- ✅ All original functionality preserved

### Streaming Component (telegram_video_streamer.py)
- ✅ Receives videos from search.py
- ✅ Generates public streaming links
- ✅ HTTP range request support (seek, pause, resume)
- ✅ Memory-efficient streaming from Telegram CDN
- ✅ All original functionality preserved

## Setup Instructions

### 1. Install Dependencies

```bash
pip install telethon aiogram pyrogram fastapi uvicorn httpx python-dotenv jinja2 tgcrypto uvloop
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Get from https://my.telegram.org/apps
API_ID=your_api_id
API_HASH=your_api_hash

# Get from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token

# Your streaming bot username
STREAMING_BOT_USERNAME=@your_streaming_bot

# Your public domain (or localhost for testing)
DOMAIN=http://localhost:8000
```

### 3. Create Your Streaming Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token to `.env` as `TELEGRAM_BOT_TOKEN`
5. Copy the bot username to `.env` as `STREAMING_BOT_USERNAME`

## Usage

### Running the Streaming Service

Start the streaming service first:

```bash
cd redmoon-stream-master
python telegram_video_streamer.py
```

The service will start on `http://localhost:8000`

### Running the Search Tool

In a new terminal, run the search tool:

```bash
python search.py
```

### Workflow

1. **Start search.py**
   - It will ask if you want to forward to the streaming bot (default: Yes)
   - Enter movie name to search

2. **Search for movies**
   - Browse results using button navigation
   - Select the movie you want

3. **Automatic forwarding**
   - Video is automatically forwarded to your streaming bot
   - Streaming bot generates a public link

4. **Access the stream**
   - Check your streaming bot messages for the watch link
   - Open the link in any browser to stream

## Integration Points

### Shared Configuration (`config.py`)
- Centralized environment variable management
- Used by both search.py and telegram_video_streamer.py
- Ensures consistent credentials across both systems

### File Flow
```
TheProSearchBot → search.py → Streaming Bot → telegram_video_streamer.py → Public Link
```

### No Conflicts
- ✅ Different Telegram libraries (telethon, aiogram, pyrogram) coexist
- ✅ Separate session files prevent conflicts
- ✅ Independent async event loops
- ✅ Modular architecture allows running separately or together

## Advanced Configuration

### Custom Search Bot
Change the search bot in `.env`:
```env
SEARCH_BOT_USERNAME=YourCustomSearchBot
```

### Custom Domain
For production deployment, update the domain:
```env
DOMAIN=https://your-domain.com
```

### Manual Forwarding
If you prefer to manually choose where to forward files:
- Leave `STREAMING_BOT_USERNAME` empty in `.env`
- search.py will ask for username each time

## Troubleshooting

### "Configuration errors" message
- Ensure all required variables are set in `.env`
- Run `python config.py` to validate configuration

### "Module not found: config"
- Ensure `config.py` is in the same directory as `search.py`
- For `telegram_video_streamer.py`, ensure parent directory is accessible

### Streaming bot not receiving files
- Verify `STREAMING_BOT_USERNAME` is correct (include @)
- Ensure the bot is started and running
- Check that you've sent `/start` to your bot at least once

### Videos not streaming
- Ensure `telegram_video_streamer.py` is running
- Check that the domain in `.env` matches your server
- Verify file size is included in the URL

## File Structure

```
BBHC-Theatre/
├── config.py                    # Shared configuration
├── search.py                    # Search tool (updated)
├── .env                         # Your credentials (create from .env.example)
├── .env.example                 # Template for environment variables
├── INTEGRATION_GUIDE.md         # This file
└── redmoon-stream-master/
    ├── telegram_video_streamer.py  # Streaming service (updated)
    └── templates/
        ├── watch.html           # Video player page
        └── watch.css            # Styles
```

## Benefits of Integration

1. **Seamless Workflow**: Search → Forward → Stream in one flow
2. **No Manual Steps**: Automatic forwarding to streaming bot
3. **Preserved Functionality**: All original features intact
4. **Modular Design**: Can run components independently
5. **Shared Config**: Single source of truth for credentials
6. **No Conflicts**: Clean separation of concerns

## Next Steps

- Set up a public domain for production use
- Configure reverse proxy (nginx) for HTTPS
- Add authentication to streaming endpoints
- Implement caching for frequently accessed videos
- Add analytics and usage tracking

## Support

For issues or questions:
1. Check this guide first
2. Verify `.env` configuration
3. Check console logs for errors
4. Ensure all dependencies are installed
