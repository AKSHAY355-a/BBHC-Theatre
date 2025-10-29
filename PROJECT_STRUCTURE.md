# Project Structure - Cloud Theatre (BBHC-Theatre)

## 📁 Clean Project Structure

```
BBHC-Theatre/
│
├── 🔧 Configuration Files
│   ├── .env                          # Your credentials (DO NOT COMMIT)
│   ├── .env.example                  # Template for environment variables
│   ├── config.py                     # Shared configuration module
│   └── requirements.txt              # Python dependencies
│
├── 🎬 Core Application Files
│   ├── search.py                     # Movie search tool (integrated)
│   └── index.html                    # Web interface (if needed)
│
├── 📺 Streaming Service
│   └── redmoon-stream-master/
│       ├── telegram_video_streamer.py    # Streaming bot & FastAPI server
│       └── templates/
│           ├── watch.html                # Video player page
│           └── watch.css                 # Player styles
│
├── 📚 Documentation
│   ├── README.md                     # Original project documentation
│   ├── INTEGRATION_GUIDE.md          # Integration setup guide
│   └── PROJECT_STRUCTURE.md          # This file
│
├── 🗑️ Files to Remove/Ignore
│   ├── .env.example                  # Can be removed after creating .env
│   ├── prosearch_single.session*     # Auto-generated session files (gitignore)
│   ├── video_streamer_bot.session*   # Auto-generated session files (gitignore)
│   ├── __pycache__/                  # Python cache (gitignore)
│   ├── myenv/                        # Virtual environment (gitignore)
│   └── redmoon-stream-master/
│       ├── social_posts.txt          # Marketing content (not needed)
│       └── .gitignore                # Duplicate gitignore
│
└── 🎨 Frontend Assets (if using web interface)
    ├── css/
    └── js/
```

## 📋 File Categories

### ✅ Essential Files (Keep)
- **config.py** - Shared configuration
- **search.py** - Search functionality
- **telegram_video_streamer.py** - Streaming service
- **requirements.txt** - Dependencies
- **.env** - Your credentials
- **templates/** - Video player UI

### 📖 Documentation (Keep)
- **README.md** - Project info
- **INTEGRATION_GUIDE.md** - Setup instructions
- **PROJECT_STRUCTURE.md** - This file

### 🗑️ Can Be Removed
- **social_posts.txt** - Marketing content (not needed for functionality)
- **.env.example** - Already copied to .env (keep if sharing project)

### 🚫 Auto-Generated (Add to .gitignore)
- **prosearch_single.session*** - Telethon session files
- **video_streamer_bot.session*** - Pyrogram session files
- **__pycache__/** - Python bytecode cache
- **myenv/** - Virtual environment
- **.git/** - Git repository

## 🔐 Security Notes

### Never Commit These Files:
```
.env
*.session
*.session-journal
__pycache__/
myenv/
```

### Safe to Commit:
```
.env.example
config.py
search.py
telegram_video_streamer.py
requirements.txt
templates/
*.md
```

## 📊 File Sizes Overview

### Large Files (Consider .gitignore):
- Session files: ~28-45 KB each
- Virtual environment: Can be 100+ MB
- __pycache__: Varies

### Small Files (Safe to track):
- Python scripts: 10-12 KB
- Config files: < 2 KB
- Templates: < 1 KB

## 🎯 Recommended Actions

1. **Create .gitignore** (if not exists):
   ```
   .env
   *.session
   *.session-journal
   __pycache__/
   myenv/
   venv/
   *.pyc
   .DS_Store
   ```

2. **Remove unnecessary files**:
   - `redmoon-stream-master/social_posts.txt`
   - Keep `.env.example` if sharing project

3. **Keep organized**:
   - All Python scripts in root or organized folders
   - All docs in root for easy access
   - Templates in subdirectory

## 🚀 Quick Start Files

To run the integrated system, you only need:
1. `.env` (with credentials)
2. `config.py`
3. `search.py`
4. `redmoon-stream-master/telegram_video_streamer.py`
5. `redmoon-stream-master/templates/`
6. `requirements.txt` (for dependencies)

Everything else is either documentation or auto-generated!
