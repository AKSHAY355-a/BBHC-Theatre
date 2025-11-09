"""
Shared configuration for Telegram Video Streaming System
Loads environment variables for both search.py and telegram_video_streamer.py
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram API credentials (shared by both systems)
API_ID = os.getenv("API_ID", "26840260")
API_HASH = os.getenv("API_HASH", "b38ca5e47129f33da3b4d2dcb5700aa0")

# Bot credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SEARCH_BOT_USERNAME = os.getenv("SEARCH_BOT_USERNAME", "TheProSearchBot")

# Streaming bot configuration (optional - not needed for RedMoon)
STREAMING_BOT_USERNAME = os.getenv("STREAMING_BOT_USERNAME")

# RedMoon Stream server URL
REDMOON_STREAM_URL = os.getenv("REDMOON_STREAM_URL", "http://localhost:8000")

# Domain for public streaming links
DOMAIN = os.getenv("DOMAIN", "http://localhost:8000")

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    
    if not STREAMING_BOT_USERNAME:
        errors.append("STREAMING_BOT_USERNAME is required for integration")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

# Only validate when explicitly called (not on import)
if __name__ == "__main__":
    validate_config()
    print("✅ Configuration is valid!")
