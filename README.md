# 📺 JioTV PRO Bot — 『𝗠𝗔𝗗𝗔𝗥𝗔』

A feature-rich **Telegram bot** for recording live **JioTV channels**, downloading **catchup TV**, browsing **EPG guide**, and managing **multiple audio tracks** — all without login!

---

## 🎯 Features

✅ **Live Recording** — Record any JioTV channel in your desired quality  
✅ **Catchup TV** — Download missed episodes from available catchup channels  
✅ **EPG Guide** — Browse full TV schedule for any channel  
✅ **Multi-Audio** — Choose specific audio tracks or record all at once  
✅ **Quality Selection** — Pick resolution on-the-fly (360p, 480p, 720p, 1080p)  
✅ **Scene-Style Filenames** — Professional naming: `CHANNEL.[DD-MM-YYYY].[HH.MM-HH.MM].QUALp.JioTV.WEB-DL.LANGS.AAC.2.0.H264-『𝗠𝗔𝗗𝗔𝗥𝗔』.mkv`  
✅ **Auto Token Refresh** — Automatic credential renewal every ~1.9 hours  
✅ **Channel Search** — Find channels by name instantly  
✅ **Genre Browser** — Browse channels organized by category  
✅ **Admin Panel** — Broadcast messages to all users  
✅ **MongoDB Logging** — Track user activity and statistics  

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- `ffmpeg` and `ffprobe` installed on system
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- MongoDB connection string (optional, for user tracking)

### 1️⃣ Clone & Install Dependencies

```bash
git clone https://github.com/hdmovie7080/JioTV07.git
cd JioTV07
pip install -r requirements.txt
```

### 2️⃣ Configure Bot Credentials

Edit `bot.py` and update:

```python
API_ID    = YOUR_API_ID           # Get from https://my.telegram.org/apps
API_HASH  = "YOUR_API_HASH"       # Get from https://my.telegram.org/apps
BOT_TOKEN = "YOUR_BOT_TOKEN"      # Get from @BotFather
ADMIN_ID  = YOUR_TELEGRAM_ID      # Your Telegram user ID
DB_URL    = "mongodb+srv://..."   # Optional MongoDB connection
```

### 3️⃣ Run the Bot

```bash
python bot.py
```

You should see:
```
╔══════════════════════════════════════════════════╗
║   JioTV PRO Bot  ·  『𝗠𝗔𝗗𝗔𝗥𝗔』               ║
╚══════════════════════════════════════════════════╝
   Account  : Md. Hasen Ali  (+916295958622)
   SubID    : 3126707816
   DeviceID : af4117b3b3423be4
   Admin    : 5009476236
   MongoDB  : ✅ connected
   Downloads: ./downloads
```

---

## 📋 Bot Commands

### 📺 Channel Management

| Command | Usage | Description |
|---------|-------|-------------|
| `/start` | — | Show welcome message & available commands |
| `/help` | — | Full command reference |
| `/channels` | — | Interactive genre-based channel browser |
| `/list` | — | Complete list of all channels with IDs |
| `/search` | `<name>` | Search channels by name |

**Examples:**
```
/search "star sports"
/channels → Select genre → Select channel → Quick record buttons
```

---

### ⏺ Live Recording

| Command | Usage | Description |
|---------|-------|-------------|
| `/record` | `<channel_id> <HH:MM:SS>` | Record live channel with quality/audio picker |
| `/cancel` | — | Stop active recording |

**Examples:**
```
/record 144 00:30:00     # Record for 30 minutes
/record 191 02:00:00     # Record for 2 hours (max 4 hours)
```

**Quality & Audio Picker:**
- Choose from available video resolutions
- Select specific audio tracks (default: all)
- Review before confirming

---

### 📼 Catchup TV

| Command | Usage | Description |
|---------|-------|-------------|
| `/catchup` | — | Browse catchup channels by genre |
| `/crip` | `-c <channel_id> <offset>` | Direct catchup program list |

**Offset Values:**
- `0` = Today
- `-1` = Yesterday
- `-2` = Two days ago
- etc.

**Examples:**
```
/catchup                 # Browse catchup channels
/crip -c 144 0          # Today's programs on channel 144
/crip -c 191 -1         # Yesterday's programs on channel 191
```

---

### 📡 EPG / TV Guide

| Command | Usage | Description |
|---------|-------|-------------|
| `/epg` | `<channel_id or name>` | Show today's schedule |

**Examples:**
```
/epg 144                 # By channel ID
/epg "star sports"      # By channel name (shows first match)
```

**Features:**
- Shows program times with 🔴 LIVE indicator for current shows
- Up to 20 programs listed

---

### ⚙️ Utility & Admin

| Command | Usage | Who |
|---------|-------|-----|
| `/status` | — | Check account & token expiry (All users) |
| `/refresh` | — | Force token refresh (All users) |
| `/users` | — | Get total user count (Admin only) |
| `/broadcast` | `<message>` | Send message to all users (Admin only) |

---

## 📁 Output & File Naming

All recordings are saved in `./downloads/` with professional scene-style naming:

```
CHANNEL.[DD-MM-YYYY].[HH.MM-HH.MM].QUALp.JioTV.WEB-DL.LANGS.AAC.2.0.H264-『𝗠𝗔𝗗𝗔𝗥𝗔』.mkv
```

**Example:**
```
SONY.YAY!.[01-10-2025].[06.50-08.25].720p.JioTV.WEB-DL.HIN-TAM-TEL.AAC.2.0.H264-『𝗠𝗔𝗗𝗔𝗥𝗔』.mkv
```

**Breakdown:**
- `SONY.YAY!` — Channel name (dot-separated)
- `01-10-2025` — Recording date (DD-MM-YYYY)
- `06.50-08.25` — Start & end time (HH.MM format)
- `720p` — Video quality
- `JioTV.WEB-DL` — Source tag
- `HIN-TAM-TEL` — Audio languages (ISO 639-3)
- `AAC.2.0` — Audio codec & channels
- `H264` — Video codec
- `『𝗠𝗔𝗗𝗔𝗥𝗔』` — Release tag

---

## 🔐 Security & API Keys

### JioTV Credentials
The bot uses **pre-configured** JioTV credentials (from TS-JioTV project):
- ✅ No manual login required
- ✅ Auto-refresh every ~1.9 hours
- ✅ Credentials safely embedded in code

### Telegram API
- API credentials: `my.telegram.org`
- Bot Token: From [@BotFather](https://t.me/botfather)

### MongoDB (Optional)
- Connection string: Store in environment or config
- Used only for user tracking & statistics
- Feature gracefully degrades if unavailable

---

## 🛠 Troubleshooting

### `❌ 400 Bad Request` on /channels
**Fix:** Bot will auto-refresh token. If issue persists:
```
/refresh    # Force manual refresh
/status     # Check token expiry
```

### `❌ Could not get stream URL`
**Causes:**
- Token expired → Use `/refresh`
- Channel offline
- Network timeout

**Solution:** Wait a moment and retry, or use `/refresh`

### `❌ Recording failed`
**Check:**
- FFmpeg/FFprobe installation: `ffmpeg -version`
- Disk space availability
- Check bot logs for detailed error
- Ensure quality/audio options are valid

### `❌ No catchup data for channel`
**Reasons:**
- Channel doesn't support catchup (marked 📼 in /list)
- Program too old (catchup retention ~7 days)
- API temporary unavailability

---

## 📊 Architecture

```
bot.py
├── JioTV API Integration
│   ├── fetch_channels() — Get all available channels
│   ├── fetch_epg() — Get TV schedule for a channel
│   ├── get_stream_url() — Get HLS stream URL
│   └── refresh_token() — Renew auth credentials
│
├── Recording Engine
│   ├── do_record() — Handle recording with ffmpeg
│   ├── ffprobe() — Detect stream properties
│   └── parse_probe() — Extract quality/audio info
│
├── Telegram Bot Handlers
│   ├── /command handlers
│   ├── Inline keyboard callbacks
│   └── Session management (_sess dict)
│
└── Database
    └── MongoDB user tracking (optional)
```

---

## 🎬 Recording Workflow

```
User → /record <id> <duration>
         ↓
    Probe stream (ffprobe)
         ↓
    Quality & Audio picker UI
         ↓
    User selects options
         ↓
    Start ffmpeg recording
         ↓
    Live progress updates
         ↓
    Remux TS → MKV
         ↓
    Generate thumbnail
         ↓
    Upload to Telegram
         ↓
    Clean up temp files
```

---

## 🔄 Auto Token Refresh

- Tokens auto-refresh every **6800 seconds** (~1.9 hours)
- Manual refresh: `/refresh` command
- Current token expiry: **17 Apr 2026**

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `pyrogram` | Telegram bot framework |
| `TgCrypto` | Encryption for Pyrogram |
| `pymongo` | MongoDB driver for user tracking |
| `requests` | HTTP client for JioTV APIs |
| `urllib3` | HTTP connection pooling & retries |
| `aiohttp` | Async HTTP (for streaming) |

System: `ffmpeg`, `ffprobe`

---

## 📝 Example Usage Flow

```
User: /start
Bot: Shows welcome & available commands

User: /channels
Bot: Fetches channels, shows genre list

User: Selects "Sports" genre
Bot: Shows sports channels with catchup indicator

User: Selects "Star Sports HD"
Bot: Shows quick record buttons & EPG

User: Taps "30 min" button
Bot: Probes stream → Shows quality/audio picker

User: Selects 720p + HIN + ENG audio
Bot: Starts recording with live progress

Bot: Shows progress bar with ETA & speed

Bot: Recording complete → Remuxing to MKV

Bot: Sends MKV file with metadata to Telegram

User: Receives video in Telegram ✅
```

---

## 🎨 Filename Language Codes

| Language | Code | | Language | Code |
|----------|------|---|----------|------|
| Hindi | HIN | | Tamil | TAM |
| English | ENG | | Telugu | TEL |
| Bengali | BEN | | Marathi | MAR |
| Gujarati | GUJ | | Kannada | KAN |
| Punjabi | PUN | | Malayalam | MAL |
| Urdu | URD | | Odia | ODI |

---

## 🤝 Contributing

Found a bug? Have a feature idea?  
Contact: [@II_Madara_II](https://t.me/II_Madara_II)

---

## ⚖️ Legal Notice

This bot uses **public JioTV APIs**. Usage is subject to:
- JioTV Terms of Service
- Local copyright laws
- Personal use only (not for commercial distribution)

---

## 📄 License

Project based on TS-JioTV architecture  
Bot implementation: `『𝗠𝗔𝗗𝗔𝗥𝗔』`

---

**Last Updated:** April 8, 2026  
**Status:** ✅ Fully Functional with Auto Token Refresh
