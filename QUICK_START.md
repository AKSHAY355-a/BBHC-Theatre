# Quick Start Guide - Cloud Theatre

## 🚀 First Time Setup

### 1. Login (One Time)
```powershell
python login.py
```
- Enter your admin name
- Enter phone number (10 digits, without +91)
- Enter OTP from Telegram
- ✅ Session valid for 24 hours!

### 2. Start Streaming Service
```powershell
cd redmoon-stream-master
python telegram_video_streamer.py
```
- Keep this running in one terminal
- Access at http://localhost:8000

### 3. Search Movies
```powershell
python search.py
```
- Automatically checks authentication
- Search and forward movies
- Videos sent to streaming bot

## 📋 Daily Usage (After Login)

```powershell
# Terminal 1: Streaming Service
cd redmoon-stream-master
python telegram_video_streamer.py

# Terminal 2: Search Tool
python search.py
```

## 🔐 Login System

### Auto +91 Prefix
| You Type | System Uses |
|----------|-------------|
| `9876543210` | `+919876543210` |
| `919876543210` | `+919876543210` |
| `+919876543210` | `+919876543210` |

### Session Info
- ⏰ Valid for: **24 hours**
- 💾 Stored in: `auth_session.json`
- 🔄 Auto-check: Every time you run search.py

## 🎯 Complete Workflow

```
1. Login (python login.py)
   ↓
2. Start Streaming Service
   ↓
3. Run Search Tool
   ↓
4. Search for Movies
   ↓
5. Select & Forward
   ↓
6. Get Streaming Link from Bot
   ↓
7. Watch in Browser!
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `login.py` | Authentication script |
| `login.html` | Web UI (mockup) |
| `search.py` | Movie search tool |
| `telegram_video_streamer.py` | Streaming service |
| `.env` | Your credentials |
| `auth_session.json` | Login session (auto-generated) |

## ⚡ Quick Commands

```powershell
# First time login
python login.py

# Check if logged in
python login.py

# Start streaming
cd redmoon-stream-master && python telegram_video_streamer.py

# Search movies (auto-checks login)
python search.py

# View web login UI
start login.html
```

## 🔒 Security Notes

✅ Session expires after 24 hours
✅ OTP required for every new login
✅ All session files in .gitignore
✅ No passwords stored locally

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Authentication required" | Run `python login.py` |
| "Session expired" | Login again (24 hours passed) |
| OTP not received | Check Telegram app |
| Invalid OTP | Enter exact code, no spaces |

## 📚 Documentation

- **LOGIN_GUIDE.md** - Detailed login documentation
- **INTEGRATION_GUIDE.md** - System integration guide
- **PROJECT_STRUCTURE.md** - File organization
- **CLEANUP_SUMMARY.md** - Project cleanup info

## 🎬 Example Session

```powershell
PS> python login.py
============================================================
🎬 CLOUD THEATRE - ADMIN LOGIN
============================================================
👤 Admin Name: John
📱 Phone Number (without +91): 9876543210
🔢 Enter the OTP code: 12345
✅ LOGIN SUCCESSFUL!

PS> python search.py
============================================================
🎬 CLOUD THEATRE - MOVIE SEARCH
============================================================
✅ Authenticated as: John
📱 Phone: +919876543210

Enter movie name (or 'q' to quit): Inception
🔎 Searching: Inception
...
```

## ✨ Features

- 🔐 Secure OTP authentication
- 📱 Auto +91 prefix for Indian numbers
- ⏰ 24-hour session validity
- 🎬 Movie search & forward
- 📺 Video streaming service
- 🌐 Beautiful web interface
- 🚫 No impact on existing features

---

**Ready to start? Run `python login.py` now! 🚀**
