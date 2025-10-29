# Login System Guide - Cloud Theatre

## 🔐 Overview

The Cloud Theatre now includes a secure authentication system that requires admin login before accessing the movie search functionality. Authentication is done via Telegram OTP (One-Time Password).

## 🎯 Features

- ✅ **Telegram OTP Authentication** - Secure login using your phone number
- ✅ **Auto +91 Prefix** - Indian phone numbers automatically prefixed
- ✅ **Session Management** - Stay logged in for 24 hours
- ✅ **No Functionality Impact** - All existing features work exactly as before
- ✅ **Separate Login Page** - Beautiful web interface for login
- ✅ **Command-line Login** - Python script for authentication

## 📁 New Files

```
BBHC-Theatre/
├── login.py              # Command-line login script
├── login.html            # Web-based login interface (UI only)
├── auth_session.json     # Session storage (auto-generated)
└── admin_*.session       # Telegram session files (auto-generated)
```

## 🚀 How to Use

### Method 1: Direct Login (Recommended)

1. **Run the login script**:
   ```powershell
   python login.py
   ```

2. **Enter your details**:
   - Admin Name: Your name
   - Phone Number: Your 10-digit number (without +91)

3. **Verify OTP**:
   - Check your Telegram app for the OTP code
   - Enter the code when prompted

4. **Success!**:
   - Session saved for 24 hours
   - You can now run search.py

### Method 2: Login via Search Tool

1. **Run search.py directly**:
   ```powershell
   python search.py
   ```

2. **If not authenticated**:
   - You'll be prompted to login
   - Choose 'Y' to login now
   - Follow the OTP process

3. **Continue searching**:
   - After successful login, search tool starts automatically

## 📱 Phone Number Format

The system automatically handles phone number formatting:

| You Enter | System Uses |
|-----------|-------------|
| `9876543210` | `+919876543210` |
| `919876543210` | `+919876543210` |
| `+919876543210` | `+919876543210` |

**Note**: The +91 prefix is always added automatically!

## 🌐 Web Interface (login.html)

A beautiful web-based login interface is available at `login.html`. 

**Important**: This is a UI mockup only. The actual authentication must be done via `login.py` because:
- Telegram API requires direct system access
- OTP verification needs Telethon library
- Browser cannot access Telegram MTProto protocol

**How to use**:
1. Open `login.html` in your browser to see the interface
2. For actual login, use `python login.py` in terminal

## ⏰ Session Management

### Session Duration
- **Valid for**: 24 hours from login
- **Auto-saved**: Session stored in `auth_session.json`
- **Auto-check**: Verified every time you run search.py

### Session Info
```json
{
  "admin_name": "Your Name",
  "phone": "+919876543210",
  "timestamp": "2025-10-28T23:00:00",
  "expires": "2025-10-29T23:00:00"
}
```

### Check Session Status
```powershell
python login.py
```
If you have an active session, it will show:
```
✅ Welcome back, Your Name!
📱 Phone: +919876543210
```

### Logout
To clear your session:
```python
from login import TelegramAuth
auth = TelegramAuth()
auth.logout()
```

Or simply delete `auth_session.json`

## 🔒 Security Features

1. **OTP Verification**: Every login requires Telegram OTP
2. **Session Expiry**: Automatic logout after 24 hours
3. **Secure Storage**: Session data stored locally
4. **No Password Storage**: Uses Telegram's authentication
5. **2FA Support**: Works with Telegram 2-factor authentication

## 🛠️ Troubleshooting

### "Authentication required" error
**Solution**: Run `python login.py` first

### "Session expired" message
**Solution**: Login again - your session lasted 24 hours

### OTP not received
**Solutions**:
- Check your Telegram app
- Ensure phone number is correct
- Try again after a few seconds

### "Invalid OTP code" error
**Solution**: 
- Enter the exact code from Telegram
- Don't include spaces or dashes
- Code expires after a few minutes

### 2FA password prompt
**Solution**: Enter your Telegram 2-factor authentication password

## 📊 Workflow Diagram

```
┌─────────────────┐
│  Run search.py  │
└────────┬────────┘
         │
         ▼
   ┌─────────────┐
   │ Authenticated?│
   └──────┬──────┘
          │
    ┌─────┴─────┐
    │           │
   Yes          No
    │           │
    │      ┌────▼────┐
    │      │ Login   │
    │      │ Prompt  │
    │      └────┬────┘
    │           │
    │      ┌────▼────┐
    │      │ Enter   │
    │      │ Details │
    │      └────┬────┘
    │           │
    │      ┌────▼────┐
    │      │ Verify  │
    │      │   OTP   │
    │      └────┬────┘
    │           │
    └─────┬─────┘
          │
          ▼
   ┌──────────────┐
   │ Search Movies│
   └──────────────┘
```

## 🎬 Example Usage

### First Time Login
```powershell
PS> python login.py

============================================================
🎬 CLOUD THEATRE - ADMIN LOGIN
============================================================

📝 Please enter your details:
👤 Admin Name: John Doe
📱 Phone Number (without +91): 9876543210

👤 Admin: John Doe
📱 Phone: +919876543210

🔐 Initiating Telegram authentication...
📤 Sending OTP to your phone...

🔢 Enter the OTP code you received: 12345

✅ Authentication successful!
✅ Session saved. Valid for 24 hours.

============================================================
✅ LOGIN SUCCESSFUL!
============================================================
👤 Admin: John Doe
📱 Phone: +919876543210
⏰ Session valid for: 24 hours
============================================================
```

### Subsequent Logins (Within 24 Hours)
```powershell
PS> python search.py

============================================================
🎬 CLOUD THEATRE - MOVIE SEARCH
============================================================
✅ Welcome back, John Doe!
📱 Phone: +919876543210

✅ Authenticated as: John Doe
📱 Phone: +919876543210
============================================================

✅ Client started.
📤 Files will be forwarded to streaming bot: @File_Link_Generatorr_Bot

Enter movie name (or 'q' to quit): 
```

## 🔄 Integration with Existing System

The login system is **fully integrated** and **non-intrusive**:

✅ **search.py** - Checks authentication automatically
✅ **telegram_video_streamer.py** - Works independently (no auth required)
✅ **All existing features** - Work exactly as before
✅ **Session persistence** - Login once, use for 24 hours

## 📝 Notes

1. **First-time setup**: Run `login.py` before using search.py
2. **Session file**: `auth_session.json` is auto-generated
3. **Telegram sessions**: `admin_*.session` files are created by Telethon
4. **Gitignore**: All session files are already in .gitignore
5. **No impact**: Streaming service doesn't require authentication

## 🎯 Benefits

- 🔐 **Secure**: Only authorized admins can search
- 📱 **Easy**: Simple phone + OTP login
- ⏰ **Convenient**: 24-hour session validity
- 🚫 **Non-intrusive**: Doesn't affect existing features
- 🎨 **Beautiful**: Modern web interface available

## 🆘 Support

If you encounter any issues:
1. Check this guide first
2. Ensure Telegram app is installed and working
3. Verify phone number is correct (+91 prefix)
4. Check that you have internet connection
5. Try logging out and logging in again

---

**Remember**: The login system protects your search tool while keeping all functionality intact! 🎬🔒
