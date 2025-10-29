# 🎬 BBHC Theatre - Flask Web App

## ✅ SETUP COMPLETE!

Your Flask web application is ready to run!

## 🚀 Quick Start

### 1. Start Flask App
```powershell
python app.py
```
**Access at**: http://localhost:5000

### 2. Start Streaming Service (Optional - in separate terminal)
```powershell
cd redmoon-stream-master
python telegram_video_streamer.py
```
**Runs on**: http://localhost:8000

## 🔐 Login Flow

1. Open http://localhost:5000
2. Enter admin name and phone (10 digits, no +91)
3. Receive OTP on Telegram
4. Enter OTP code
5. Redirected to BBHC Theatre!

## ✨ What's Integrated

### ✅ Completed
- **Flask Backend** (`app.py`) - All API endpoints ready
- **Login Page** - BBHC theme with OTP authentication
- **Session Management** - 24-hour sessions
- **Movie Search API** - Backend ready
- **Streaming API** - Backend ready
- **Auto +91 Prefix** - Phone number handling

### 🔄 Next: Frontend Integration
The backend is complete. Next step is to integrate the search bar in `index.html` to call the APIs.

## 📋 API Endpoints Ready

```
POST /api/send-otp          - Send OTP to phone
POST /api/verify-otp        - Verify OTP code
GET  /api/session-status    - Check login status
POST /api/search-movie      - Search for movies
POST /api/get-stream-link   - Get streaming URL
```

## 🎨 BBHC Theme Applied

Login page now uses:
- Dark background (#0a0a0a)
- Red accent (#e50914)
- Netflix-style design
- Smooth animations

## 📁 File Structure

```
BBHC-Theatre/
├── app.py                 # Flask backend ✅
├── templates/
│   ├── login.html        # BBHC themed login ✅
│   └── index.html        # Main page (needs search integration)
├── static/
│   ├── css/style.css     # BBHC theme
│   └── js/              # Frontend scripts
└── .env                  # Your credentials
```

## 🧪 Test It Now!

```powershell
# Start the app
python app.py

# Open browser
start http://localhost:5000
```

## 📝 What Happens

1. **Not logged in** → Redirects to /login
2. **Enter credentials** → Sends OTP via Telegram
3. **Verify OTP** → Creates session
4. **Redirects to /** → Main theatre page
5. **Session valid** → 24 hours

## 🎯 Next Steps

To complete the integration, we need to:
1. Add search bar functionality to `index.html`
2. Display movie results
3. Add click handlers for streaming
4. Integrate video player

**Your Flask app is ready to run!** 🚀
