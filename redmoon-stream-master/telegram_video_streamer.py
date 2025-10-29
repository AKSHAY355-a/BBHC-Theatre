"""
Telegram Video Streamer Bot + FastAPI Web Service

This application provides a Telegram bot that accepts video uploads and generates public streaming links,
along with a FastAPI web service that streams videos directly from Telegram without storing files locally.
It acts as a stateless proxy that translates browser/HTML5 range requests into Telegram CDN chunk downloads.

Features:
- Telegram bot using aiogram for handling video messages
- FastAPI web service with streaming endpoints that understand HTTP Range requests
- Memory-efficient streaming by forwarding byte ranges to Telegram without buffering full files
- HTML video player page for easy viewing and debugging
- Performance optimizations using TgCrypto and uvloop for faster streaming

Requirements:
- Python 3.8+
- Telegram bot token (set as TELEGRAM_BOT_TOKEN environment variable)
- Dependencies: aiogram, fastapi, uvicorn, httpx, tgcrypto, uvloop

Installation:
1. Install dependencies: pip install aiogram fastapi uvicorn httpx python-dotenv jinja2 pyrogram tgcrypto uvloop
2. Create a .env file in the same directory with:
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   DOMAIN=http://localhost:8000  # Or your public domain
3. Run the script: python telegram_video_streamer.py

Usage:
1. Send a video to the Telegram bot
2. Bot replies with a watch link (e.g., https://your-domain.com/watch/<file_id>)
3. Open the link in a browser to stream the video with byte-range support (seek, pause/resume)
4. The FastAPI service proxies range requests to Telegram and never stores the file locally

Note: Replace 'your-domain.com' in the code with your actual domain or localhost for testing.
"""

import asyncio
import os
import re
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Tuple

# Install uvloop for faster async performance (2-4x speedup)
# Note: uvloop is not available on Windows, but works on Linux and macOS
try:
    import uvloop
    uvloop.install()
    print("✓ uvloop installed - async operations will be 2-4x faster")
except ImportError:
    print("⚠ uvloop not available (not supported on Windows) - using standard asyncio")
    print("  For maximum performance, run this on Linux/macOS or use TgCrypto only")

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from threading import Thread
from dotenv import load_dotenv
from pyrogram import Client
import sys

# Add parent directory to path to import shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import TELEGRAM_BOT_TOKEN, API_ID, API_HASH, DOMAIN as CONFIG_DOMAIN

# Bot token from shared configuration
TOKEN = TELEGRAM_BOT_TOKEN
API_ID = API_ID
API_HASH = API_HASH

if not all([TOKEN, API_ID, API_HASH]):
    raise ValueError("TELEGRAM_BOT_TOKEN, API_ID, and API_HASH environment variables are required")


# Domain for public links
DOMAIN = CONFIG_DOMAIN

# Normalize domain to include scheme and no trailing slash to avoid bad links in Telegram
def _normalize_domain(domain: str) -> str:
    domain = domain.strip()
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    return domain.rstrip("/")

DOMAIN = _normalize_domain(DOMAIN)

# Pyrogram's stream_media uses 1 MiB (1024 * 1024) chunks by default
# This is the maximum chunk size supported by Telegram's MTProto
CHUNK_SIZE = 1024 * 1024  # 1 MiB - aligned with Telegram's maximum chunk size

_RANGE_RE = re.compile(r"bytes=(\d+)-(\d*)")


def _parse_range(range_header: str, file_size: int) -> Tuple[int, int]:
    match = _RANGE_RE.fullmatch(range_header.strip())
    if not match:
        raise HTTPException(status_code=416, detail="Invalid Range header")

    start = int(match.group(1))
    end_str = match.group(2)
    end: Optional[int]
    end = int(end_str) if end_str else file_size - 1

    if start >= file_size:
        raise HTTPException(
            status_code=416,
            detail="Requested range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    if end >= file_size:
        end = file_size - 1
    if end < start:
        raise HTTPException(status_code=416, detail="Invalid byte range")

    return start, end

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Initialize Pyrogram client
# Using a bot token for authentication
pyrogram_bot = Client(
    "video_streamer_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=TOKEN
)


# Lifespan for FastAPI to handle startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start bot polling in background
    polling_task = asyncio.create_task(dp.start_polling(bot))
    # Start Pyrogram client
    await pyrogram_bot.start()
    yield
    # Stop polling on shutdown
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    # Stop Pyrogram client
    await pyrogram_bot.stop()

app = FastAPI(lifespan=lifespan)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="templates"), name="static")


# Handler for the /start command
@dp.message(Command("start"))
async def handle_start(message: Message):
    await message.reply("Hello! Send me a video, and I will give you a link to stream it.")


# Handler for video messages
@dp.message(F.video)
async def handle_video(message: Message):
    file_id = message.video.file_id
    file_size = message.video.file_size
    # Reply with the watch link, including file size
    watch_url = f"{DOMAIN}/watch/{file_id}?size={file_size}"
    stream_url = f"{DOMAIN}/stream/{file_id}?size={file_size}"
    text = f"🎥 Your video is ready to stream! \n\n📺 Watch in browser: {watch_url} \n\n🔗 Direct stream URL: {stream_url}"
    await message.reply(text)


# Handler for video documents
@dp.message(F.document)
async def handle_document(message: Message):
    if message.document.mime_type and 'video' in message.document.mime_type:
        file_id = message.document.file_id
        file_size = message.document.file_size
        # Reply with the watch link, including file size
        watch_url = f"{DOMAIN}/watch/{file_id}?size={file_size}"
        stream_url = f"{DOMAIN}/stream/{file_id}?size={file_size}"
        text = f"🎥 Your video is ready to stream! \n\n📺 Watch in browser: {watch_url} \n\n🔗 Direct stream URL: {stream_url}"
        await message.reply(text)
    else:
        await message.reply("Please send a video.")

# FastAPI route for /watch/<file_id>
@app.get("/watch/{file_id:path}")
async def watch_video(request: Request, file_id: str, size: int = 0):
    stream_url = f"/stream/{file_id}?size={size}"
    return templates.TemplateResponse("watch.html", {"request": request, "stream_url": stream_url})

# FastAPI route for /stream/<file_id>
@app.get("/stream/{file_id:path}")
async def stream_video(file_id: str, request: Request, size: int) -> StreamingResponse:
    if size == 0:
        raise HTTPException(status_code=400, detail="Missing file size")

    file_size = size
    range_header = request.headers.get("range")

    start = 0
    end = file_size - 1
    status_code = 200
    content_length = file_size

    if range_header:
        try:
            start, end = _parse_range(range_header, file_size)
            content_length = end - start + 1
            status_code = 206
        except HTTPException as e:
            raise e

    # Pyrogram's stream_media is an async generator with optimized chunk streaming
    async def generate():
        try:
            # Calculate chunk-based offset and limit for Pyrogram
            # Pyrogram's offset is in chunks (1 MiB each), not bytes
            start_chunk = start // CHUNK_SIZE
            offset_in_chunk = start % CHUNK_SIZE
            
            # Calculate how many chunks we need to stream
            # Add 1 to handle partial chunks at the end
            total_chunks_needed = (content_length + offset_in_chunk + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            bytes_to_send = content_length
            is_first_chunk = True

            # Use stream_media with offset and limit for optimal performance
            # offset: skip chunks before the requested range
            # limit: only fetch the chunks we need (reduces unnecessary data transfer)
            async for chunk in pyrogram_bot.stream_media(
                file_id, 
                offset=start_chunk,
                limit=total_chunks_needed
            ):
                if bytes_to_send <= 0:
                    break

                # If this is the first chunk, apply the inner-chunk offset
                if is_first_chunk and offset_in_chunk > 0:
                    chunk = chunk[offset_in_chunk:]
                    is_first_chunk = False

                # Ensure we don't send more bytes than requested
                if len(chunk) > bytes_to_send:
                    yield chunk[:bytes_to_send]
                    break

                yield chunk
                bytes_to_send -= len(chunk)

        except Exception as e:
            print(f"Error in generate: {e}")
            # This part of the code is running in a generator, so we can't raise HTTPException
            # The client will see a broken connection

    headers = {
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-cache",
        "Content-Length": str(content_length),
        "Content-Type": "video/mp4",  # Assuming mp4, can be improved
    }

    if status_code == 206:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    return StreamingResponse(
        generate(),
        status_code=status_code,
        headers=headers,
    )

if __name__ == "__main__":
    # Run FastAPI with uvicorn, which will also manage the bot's lifespan
    uvicorn.run(app, host="0.0.0.0", port=8000)