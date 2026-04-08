# ⚡ Quick Start Guide (5 Minutes)

Get JioTV PRO Bot running in under 5 minutes!

---

## 🎯 What You'll Need

✅ Python 3.9+  
✅ FFmpeg installed  
✅ Telegram account  
✅ Bot token from [@BotFather](https://t.me/botfather)  

---

## 1️⃣ Get Your Telegram Credentials (2 min)

### Get API ID & API Hash
1. Go to https://my.telegram.org/apps
2. Login with your phone number
3. Create a new application
4. Note down:
   - `APP ID` (5 digits)
   - `APP HASH` (32 hex chars)

### Get Bot Token
1. Go to [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose a name & username
4. Copy the **HTTP API token** (like `123456:ABC-DEF...`)

### Get Your Admin ID
1. Go to [@userinfobot](https://t.me/userinfobot)
2. Send `/start`
3. Note your **ID** (number)

---

## 2️⃣ Install & Configure (2 min)

```bash
# Clone repo
git clone https://github.com/hdmovie7080/JioTV07.git
cd JioTV07

# Install dependencies
pip install -r requirements.txt

# Or manually:
pip install pyrogram==2.0.106 TgCrypto pymongo requests urllib3 aiohttp
```

### Configure Bot
Open `bot.py` in editor and find these lines (around line 37-40):

```python
API_ID    = 20093900                                # ← Replace with YOUR API_ID
API_HASH  = "314286d8af54eda517ff6f3974fd3aad"   # ← Replace with YOUR API_HASH
BOT_TOKEN = "8516486280:AAHi3kgQ75gvJYJDUpSv_E8Q5DfNVK58fPs"  # ← Replace with YOUR TOKEN
ADMIN_ID  = 5009476236                             # ← Replace with YOUR ID
```

**That's it!** No other changes needed.

---

## 3️⃣ Run (1 min)

```bash
python bot.py
```

**Expected output:**
```
╔══════════════════════════════════════════════════╗
║   JioTV PRO Bot  ·  『𝗠𝗔𝗗𝗔𝗥𝗔』               ║
╚══════════════════════════════════════════════════╝
   Account  : Md. Hasen Ali  (+916295958622)
   SubID    : 3126707816
   DeviceID : af4117b3b3423be4
   Admin    : YOUR_ID_HERE
   MongoDB  : ❌ disabled
   Downloads: ./downloads
```

✅ **Bot is running!**

---

## 🎬 Test It Out

Open Telegram and send your bot:

```
/start
```

You should see the welcome message!

---

## 📺 Try Commands

```
/list              # See all channels
/search sony       # Search for Sony channels
/channels          # Browse by genre
/epg 144           # See TV schedule
/record 144 00:30:00   # Record 30 minutes (you'll get quality picker)
```

---

## ❌ Troubleshooting Quick Fixes

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from ffmpeg.org
```

### Bot doesn't respond
1. Make sure token is correct in `bot.py`
2. Restart: `Ctrl+C` then `python bot.py`
3. Check if `/start` returns an error

### "400 Bad Request" on /channels
Bot auto-recovers now! Just wait a moment and try again.

---

## 📚 Learn More

- 📖 [Full README](README.md) — Complete guide
- 🔧 [Troubleshooting](TROUBLESHOOTING.md) — Common issues
- 🚀 [Deployment](DEPLOYMENT.md) — Run 24/7 on VPS/Docker
- ⚙️ [Config Template](config_template.py) — Advanced setup

---

## 🎉 You're Done!

Your JioTV PRO Bot is running!

**Now you can:**
- 📺 Record live TV
- 📼 Download catchup shows  
- 📡 Browse TV schedule
- 🎞️ Pick quality & audio tracks
- 📤 Auto-upload to Telegram

---

## 💡 Pro Tips

**Tip 1:** Run in background
```bash
nohup python bot.py &   # Linux/macOS
```

**Tip 2:** Run 24/7 with systemd
See [DEPLOYMENT.md](DEPLOYMENT.md) → "Linux Server (VPS)"

**Tip 3:** Use Docker
```bash
docker run -d --name jiotv -v $(pwd)/downloads:/app/downloads hdmovie7080/jiotv-bot
```

**Tip 4:** Record long videos
```
/record 144 04:00:00   # 4 hours (max allowed)
```

---

## ⚡ Commands Cheat Sheet

| Command | What it does |
|---------|------------|
| `/start` | Welcome message |
| `/channels` | Browse by genre |
| `/list` | All channels |
| `/search NAME` | Find channel |
| `/record ID DUR` | Record live |
| `/catchup` | Catchup shows |
| `/crip -c ID OFS` | Catchup programs |
| `/epg ID` | TV schedule |
| `/status` | Token status |
| `/refresh` | Refresh token |
| `/cancel` | Stop recording |

---

## 📞 Need Help?

Contact: [@II_Madara_II](https://t.me/II_Madara_II)

Include:
- What you tried
- Error message (if any)
- Last 5 lines of output

---

## ✅ Verification Checklist

- [ ] API credentials from my.telegram.org
- [ ] Bot token from @BotFather
- [ ] Credentials entered in bot.py
- [ ] pip install -r requirements.txt done
- [ ] FFmpeg installed
- [ ] `python bot.py` runs without errors
- [ ] Bot responds to /start in Telegram
- [ ] Successfully ran a command like /list

If all checked ✅ — you're good to go!

---

**Time to setup:** ~5 minutes  
**Difficulty:** 🟢 Very Easy  
**Status:** ✅ Ready to use!

Enjoy recording JioTV! 📺✨
