# BBHC Theatre Backend

FastAPI backend that integrates Telegram search and streaming functionality.

## Architecture

```
Browser → FastAPI Backend → Telegram (Search Bot) → Streaming Bot → Video Stream
```

## Components

### 1. **main.py** - FastAPI Application
- `/api/search?q=query` - Search for movies
- `/api/stream` - Request streaming URL
- `/api/job/{job_id}` - Check streaming job status
- `/health` - Health check endpoint

### 2. **telegram_service.py** - Telegram Integration
- Manages single Telethon client session
- Handles search bot interactions
- Clicks inline buttons and processes callbacks
- Forwards videos to streaming bot
- Extracts streaming URLs from responses

### 3. **job_manager.py** - Job Queue
- Tracks async streaming requests
- Stores job status (pending → processing → done/failed)
- Provides job status polling

### 4. **models.py** - Data Models
- Pydantic models for API requests/responses
- Type-safe data validation

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure `.env` file has:
```
API_ID=your_api_id
API_HASH=your_api_hash
SEARCH_BOT_USERNAME=TheProSearchBot
STREAMING_BOT_USERNAME=your_streaming_bot
TELEGRAM_BOT_TOKEN=your_bot_token
DOMAIN=http://localhost:8000
```

### 3. Authenticate Telegram Session
First time only - run from project root:
```bash
python login.py
```

## Running the Backend

### Start Backend Server (Port 5000)
```bash
cd backend
python main.py
```

Or from project root:
```bash
python -m backend.main
```

### Start Streaming Server (Port 8000)
In a separate terminal:
```bash
cd redmoon-stream-master
python telegram_video_streamer.py
```

### Open Frontend
Open `index.html` in browser or serve with:
```bash
python -m http.server 3000
```

## API Usage

### Search Movies
```bash
curl "http://localhost:5000/api/search?q=Inception"
```

Response:
```json
{
  "query": "Inception",
  "results": [
    {
      "id": "msg_123_456",
      "title": "Inception 2010",
      "qualities": [
        {"label": "480p", "type": "callback", "value": "0,0"},
        {"label": "720p", "type": "callback", "value": "0,1"}
      ]
    }
  ],
  "total": 1
}
```

### Request Stream
```bash
curl -X POST http://localhost:5000/api/stream \
  -H "Content-Type: application/json" \
  -d '{"item_id": "msg_123_456", "quality_index": 0}'
```

Response:
```json
{
  "job_id": "abc-123-def",
  "status": "pending"
}
```

### Check Job Status
```bash
curl "http://localhost:5000/api/job/abc-123-def"
```

Response:
```json
{
  "job_id": "abc-123-def",
  "status": "done",
  "stream_url": "http://localhost:8000/stream/xyz123?size=12345",
  "progress": "Stream ready"
}
```

## Data Flow

1. **User searches "Inception"**
   - Frontend → `GET /api/search?q=Inception`
   - Backend sends query to `@TheProSearchBot`
   - Bot replies with results + inline buttons
   - Backend parses and returns JSON

2. **User clicks quality button**
   - Frontend → `POST /api/stream {item_id, quality_index}`
   - Backend creates job and clicks Telegram button
   - Bot sends file or /start link
   - Backend forwards to streaming bot
   - Streaming bot returns HTTP URL
   - Backend stores URL in job

3. **Frontend polls job**
   - Frontend → `GET /api/job/{job_id}` (every 1s)
   - When status=done, receives `stream_url`
   - Plays video in HTML5 player

## Security

- ✅ API credentials never exposed to browser
- ✅ All Telegram operations server-side
- ✅ CORS configured for frontend origin
- ✅ Session files stored securely
- ✅ Rate limiting recommended for production

## Troubleshooting

### "Telegram client not started"
- Ensure you ran `python login.py` first
- Check session file exists: `bbhc_backend.session`

### "Search failed"
- Verify `SEARCH_BOT_USERNAME` in `.env`
- Check Telegram session is valid
- Ensure bot is accessible

### "Stream job failed"
- Check streaming bot is running (port 8000)
- Verify `STREAMING_BOT_USERNAME` in `.env`
- Check backend logs for errors

### Port already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

## Production Deployment

### Use Redis for Job Queue
```python
# Install: pip install redis
from redis import Redis
redis_client = Redis(host='localhost', port=6379)
```

### Add Rate Limiting
```python
# Install: pip install slowapi
from slowapi import Limiter
limiter = Limiter(key_func=lambda: "global")
```

### Use HTTPS
- Deploy behind nginx reverse proxy
- Use Let's Encrypt for SSL certificates

### Environment Variables
- Never commit `.env` to git
- Use environment-specific configs
- Rotate API keys regularly

## Development

### Hot Reload
Backend auto-reloads on file changes:
```bash
python main.py  # uvicorn with reload=True
```

### Debug Mode
Set in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=5000, reload=True, log_level="debug")
```

### Testing
```bash
# Test search endpoint
curl "http://localhost:5000/api/search?q=test"

# Test health
curl "http://localhost:5000/health"
```
