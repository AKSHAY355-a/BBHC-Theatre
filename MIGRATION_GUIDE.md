# Migration Guide: CLI to FastAPI Backend

## Overview

This guide explains the migration from CLI-based `search.py` to the new FastAPI backend architecture.

## What Changed

### Before (CLI-based)
```
User → search.py (CLI) → Telegram → Manual forwarding → Streaming bot
```

### After (API-based)
```
Browser → FastAPI Backend → Telegram → Auto-forwarding → Streaming bot → Browser
```

## New Architecture Benefits

✅ **Web-based UI** - No more CLI, everything in browser  
✅ **Real-time search** - Instant results from Telegram  
✅ **Quality selection** - Choose video quality before streaming  
✅ **Progress tracking** - See streaming job status  
✅ **Secure** - API credentials never exposed to browser  
✅ **Scalable** - Can add Redis, multiple workers later  

## File Changes

### ✅ New Files (Keep)
```
backend/
├── __init__.py          # Package init
├── main.py              # FastAPI app
├── models.py            # Data models
├── telegram_service.py  # Telegram operations
├── job_manager.py       # Job queue
└── README.md            # Backend docs

start_backend.bat        # Start backend only
start_all.bat            # Start all services
MIGRATION_GUIDE.md       # This file
```

### 📝 Modified Files
```
js/app.js                # Now uses backend API
index.html               # Added quality selector
css/style.css            # Added quality button styles
requirements.txt         # Added FastAPI dependencies
```

### ⚠️ Deprecated Files (Can Remove Later)
```
search.py                # Replaced by backend/main.py
login.py                 # Auth now in backend (optional)
app.py                   # Flask app (optional, can merge)
```

### ✅ Unchanged Files (Keep As-Is)
```
redmoon-stream-master/   # Streaming server - perfect!
config.py                # Configuration
.env                     # Environment variables
css/                     # Styles
static/                  # Static assets
```

## Migration Steps

### Step 1: Install New Dependencies
```bash
pip install -r requirements.txt
```

This adds:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `pydantic` - Data validation

### Step 2: Ensure Telegram Session Exists
```bash
# If you haven't logged in yet:
python login.py
```

This creates `bbhc_backend.session` for the backend to use.

### Step 3: Start Backend Server
```bash
# Option A: Use startup script
start_backend.bat

# Option B: Manual start
cd backend
python main.py
```

Backend will start on **http://localhost:5000**

### Step 4: Start Streaming Server
```bash
# In a new terminal
cd redmoon-stream-master
python telegram_video_streamer.py
```

Streamer will start on **http://localhost:8000**

### Step 5: Open Frontend
```bash
# Option A: Direct file
# Just open index.html in browser

# Option B: Local server (recommended)
python -m http.server 3000
# Then open http://localhost:3000
```

### Step 6: Test the Flow
1. **Search** - Type "Inception" in search bar
2. **View Results** - Click on a movie card
3. **Select Quality** - Choose quality button in modal
4. **Stream** - Click "Start Streaming"
5. **Watch** - Video plays in browser

## Configuration

### Backend API URL
In `js/app.js`:
```javascript
this.API_BASE_URL = 'http://localhost:5000';
this.USE_BACKEND = true; // Set to false for mock data
```

### Environment Variables
In `.env`:
```bash
# Required for backend
API_ID=your_api_id
API_HASH=your_api_hash
SEARCH_BOT_USERNAME=TheProSearchBot
STREAMING_BOT_USERNAME=your_streaming_bot

# Required for streamer
TELEGRAM_BOT_TOKEN=your_bot_token
DOMAIN=http://localhost:8000
```

## API Endpoints

### Search Movies
```http
GET /api/search?q=movie_name
```

Returns:
```json
{
  "query": "Inception",
  "results": [
    {
      "id": "msg_123_456",
      "title": "Inception 2010",
      "qualities": [
        {"label": "480p", "type": "callback", "value": "0,0"}
      ]
    }
  ]
}
```

### Request Stream
```http
POST /api/stream
Content-Type: application/json

{
  "item_id": "msg_123_456",
  "quality_index": 0
}
```

Returns:
```json
{
  "job_id": "abc-123",
  "status": "pending"
}
```

### Check Job Status
```http
GET /api/job/{job_id}
```

Returns:
```json
{
  "job_id": "abc-123",
  "status": "done",
  "stream_url": "http://localhost:8000/stream/xyz?size=123"
}
```

## Troubleshooting

### Backend won't start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`  
**Fix**: `pip install -r requirements.txt`

**Error**: `Telegram client not started`  
**Fix**: Run `python login.py` first

### Search returns no results
**Check**:
1. Backend is running (http://localhost:5000/health)
2. Telegram session is valid
3. `SEARCH_BOT_USERNAME` is correct in `.env`
4. Check backend console for errors

### Streaming fails
**Check**:
1. Redmoon streamer is running (port 8000)
2. `STREAMING_BOT_USERNAME` is correct
3. Backend can forward to streaming bot
4. Check job status: `GET /api/job/{job_id}`

### CORS errors in browser
**Error**: `Access to fetch blocked by CORS policy`  
**Fix**: Backend already has CORS enabled. If still failing:
```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Already set
    ...
)
```

### Port already in use
```bash
# Windows - Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in backend/main.py
uvicorn.run(app, host="0.0.0.0", port=5001)
```

## Comparison: Old vs New

### Old Way (search.py)
```bash
$ python search.py
Enter movie name: Inception
[Shows results in terminal]
Select button index: 1
[Forwards to streaming bot]
[Copy URL manually]
[Paste in browser]
```

### New Way (Browser)
```
1. Type "Inception" in search box
2. Click movie card
3. Select quality
4. Click "Start Streaming"
5. Video plays automatically
```

## Performance

### Backend Response Times
- Search: ~2-5 seconds (Telegram bot response time)
- Stream request: ~5-10 seconds (forwarding + URL extraction)
- Job polling: ~1 second intervals

### Optimization Tips
1. **Use Redis** for job queue (multi-instance)
2. **Cache search results** (reduce Telegram calls)
3. **WebSocket** instead of polling (real-time updates)
4. **CDN** for static assets

## Rollback Plan

If you need to go back to the old CLI system:

1. **Stop backend**: Close terminal or Ctrl+C
2. **Use search.py**: `python search.py`
3. **Set frontend to mock mode**:
   ```javascript
   // In js/app.js
   this.USE_BACKEND = false;
   ```

All old files are still present and functional.

## Next Steps

### Recommended Enhancements
1. **Add authentication** - Protect API with API keys
2. **Implement caching** - Redis for search results
3. **Add WebSocket** - Real-time job updates
4. **Deploy to cloud** - Heroku, Railway, or VPS
5. **Add analytics** - Track popular searches
6. **Improve UI** - Add filters, sorting, favorites

### Production Checklist
- [ ] Set `allow_origins` to specific domain
- [ ] Add rate limiting
- [ ] Use HTTPS
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Add error tracking (Sentry)
- [ ] Use environment-specific configs
- [ ] Set up CI/CD pipeline

## Support

### Logs Location
- **Backend**: Console output
- **Streamer**: Console output
- **Frontend**: Browser DevTools → Console

### Debug Mode
```python
# In backend/main.py
uvicorn.run(app, log_level="debug")
```

### Health Check
```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "healthy",
  "telegram_connected": true
}
```

## Summary

You now have a modern, web-based streaming platform with:
- ✅ FastAPI backend handling all Telegram operations
- ✅ Real-time search and streaming
- ✅ Quality selection
- ✅ Progress tracking
- ✅ Secure API architecture
- ✅ Scalable design

The old CLI tools (`search.py`, `login.py`) are still available but no longer needed for normal operation.

**Enjoy your new streaming platform! 🎬**
