# 🔧 Troubleshooting Guide

Complete troubleshooting guide for common JioTV PRO Bot issues.

---

## 🚨 Common Errors & Solutions

### 1. `400 Client Error: Bad Request` on /channels or /epg

**Error Message:**
```
[ERROR] fetch_channels: 400 Client Error: Bad Request for url: https://jiotvapi.cdn.jio.com/apis/v1.3/getepg/get?offset=-1&channel_id=all
```

**Causes:**
- Expired authentication token
- Missing required headers
- API server temporarily unavailable
- Incorrect channel ID format

**Solutions:**

**Step 1: Refresh Token**
```
/refresh
```
Bot will auto-refresh but you can force it manually.

**Step 2: Check Status**
```
/status
```
Verify token hasn't expired. Should show: `✅ Valid`

**Step 3: Wait & Retry**
- Bot will auto-retry with exponential backoff
- Wait 2-3 minutes and try again
- API may have temporary issues

**Step 4: Restart Bot**
```bash
# Kill the bot
Ctrl+C

# Restart
python bot.py
```

**Step 5: Check Code**
Verify in `bot.py` that `_epg_headers()` includes all required tokens:
```python
def _epg_headers() -> dict:
    return {
        "Host":            "jiotvapi.cdn.jio.com",
        "user-agent":      "okhttp/4.12.13",
        "Accept-Encoding": "gzip",
        "accesstoken":     _CREDS["authToken"],      # ✅ Required
        "ssotoken":        _CREDS["ssoToken"],        # ✅ Required
        "subscriberid":    _CREDS["subscriberId"],    # ✅ Required
        "deviceId":        _CREDS["deviceId"],        # ✅ Required
        "uniqueId":        _CREDS["uniqueId"],        # ✅ Required
    }
```

---

### 2. `❌ Could not get stream URL`

**Appears When:**
- Recording `/record` command
- Downloading catchup program
- Trying to probe stream quality

**Causes:**
- Token expired (most common)
- Channel is offline
- Network connectivity issue
- JioTV server temporarily down

**Solutions:**

```
/refresh    # Refresh token first
/status     # Check if token is valid
/record 144 00:30:00  # Try again
```

If still failing:
1. Check internet connection: `ping google.com`
2. Verify FFmpeg is installed: `ffmpeg -version`
3. Try a different channel: `/list` → pick another channel
4. Wait a moment (API may be rate-limited)

---

### 3. `❌ Token refresh failed`

**Error:**
```
[ERROR] Token refresh: All attempts failed
```

**Causes:**
- Refresh token is invalid/expired
- JioTV auth server is down
- Network timeout

**Solutions:**

**Check Logs:**
```python
# In bot.py, search for token refresh logs:
log.info("✅ authToken refreshed successfully")  # Good ✅
log.error("Token refresh: All attempts failed")  # Bad ❌
```

**Update Credentials:**
If refresh token has expired (usually after 30+ days), you need to update:
1. Get fresh credentials from TS-JioTV project
2. Update in `bot.py` lines 53-105:
```python
_CREDS: Dict = {
    "authToken": "...",      # Update this
    "ssoToken": "...",       # Update this
    "refreshToken": "...",   # Update this (most important!)
    ...
}
```

3. Restart bot

---

### 4. `❌ Recording failed`

**Appears When:**
- ffmpeg encoding fails
- Disk space full
- Invalid quality/audio selection
- Stream interrupted

**Solutions:**

**Check FFmpeg Installation:**
```bash
ffmpeg -version
ffprobe -version
```

If not installed:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Check Disk Space:**
```bash
df -h  # Linux/macOS
dir C:  # Windows
```

Need at least **5-10 GB** free for 2-4 hour recordings.

**Try Different Quality:**
- Bot shows quality picker before recording
- Select **lower quality** (360p instead of 1080p)
- Select **fewer audio tracks**

**Check Bot Logs:**
Look for ffmpeg error details:
```
[ERROR] do_record error: ...
```

---

### 5. `❌ No catchup channels found`

**When Using:** `/catchup`

**Causes:**
- No channels have catchup enabled
- Catchup data not loaded yet
- API returned empty list

**Solutions:**

**Check /list Command:**
```
/list
```
Channels with catchup show 📼 marker

**Use /crip Instead:**
```
/crip -c 144 0
```
Directly query a specific channel

**Verify Channel:**
```
/search "sony"
```
Check if the channel has 📼 indicator

---

### 6. `❌ Session expired` on buttons

**When:** Tapping buttons in channel picker

**Causes:**
- Session data cleared (bot restarted)
- Message too old (sessions expire)
- Button was from previous bot instance

**Solutions:**
- Start fresh command: `/channels` or `/record`
- Don't wait too long after seeing buttons (< 5 min)

---

### 7. `⚠️ MongoDB: [error]`

**Appears On Startup:**
```
[WARNING] ⚠️  MongoDB: ...error...
```

**Causes:**
- MongoDB connection string invalid
- Network can't reach MongoDB server
- Credentials wrong

**Solutions:**

**Option A: Fix MongoDB Connection**
Update `DB_URL` in bot.py:
```python
DB_URL = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

Test connection: `mongodb+srv://...` URLs must use username:password

**Option B: Disable MongoDB (Recommended for Testing)**
```python
# In bot.py, comment out:
# _mc = pymongo.MongoClient(DB_URL)

# Or set DB_URL = "" (empty string)
```

Bot will work fine without MongoDB (user tracking just won't work).

---

### 8. `❌ Could not fetch channels` on startup

**When:** Starting `/channels`

**Likely Cause:** Very first time, may take 10-15 seconds

**Solutions:**
- Wait a bit, channel list might be loading
- Use `/refresh` then try again
- Check: `[INFO] ✅ Fetched X channels` in logs

---

### 9. `ModuleNotFoundError: No module named 'pyrogram'`

**When:** Starting bot with `python bot.py`

**Solution:**
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pyrogram==2.0.106 TgCrypto pymongo requests urllib3 aiohttp
```

---

### 10. `⚠️ FFmpeg timeout` during recording

**Error:**
```
[WARNING] ffmpeg: Command timed out
```

**Causes:**
- Internet connection too slow
- Stream interrupted
- FFmpeg processing takes too long

**Solutions:**
- Select lower quality (480p instead of 1080p)
- Select fewer audio tracks
- Increase timeout in bot code:
```python
# In bot.py, find ffmpeg calls:
subprocess.run([...], timeout=600)  # Change 600 to 1200
```

---

## 📊 Checking Bot Health

### Get Status
```
/status
```

Shows:
- Account name & mobile
- Subscriber ID & Device ID
- ✅ Valid or ❌ Expired token
- Token expiry date
- Active recording count

### Force Token Refresh
```
/refresh
```

Should show:
```
✅ Token refreshed successfully!
```

### Check Logs

**Recent Logs:**
```bash
# Last 50 lines
tail -50 /path/to/bot/logs

# Or just restart bot to see startup logs
python bot.py
```

**Look For:**
```
✅ authToken refreshed                    # Good
✅ MongoDB connected                       # Good
✅ Fetched 300 channels                   # Good
❌ fetch_channels: 400 Client Error        # Bad - retry
❌ Token refresh: All attempts failed      # Bad - update creds
```

---

## 🔍 Debug Mode

Enable detailed logging by adding to bot.py:

```python
import logging

# Change from:
logging.basicConfig(level=logging.INFO, ...)

# To:
logging.basicConfig(level=logging.DEBUG, ...)  # More verbose
```

Now you'll see ALL network requests and responses.

---

## 📋 Prerequisite Checklist

Before troubleshooting, verify:

- [ ] Python 3.9+ installed: `python --version`
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] Dependencies installed: `pip list | grep pyrogram`
- [ ] Bot token valid: `/start` gets response
- [ ] Telegram can reach bot
- [ ] Internet connection stable
- [ ] Disk space > 5GB: `df -h`
- [ ] Ports not blocked (Telegram uses 443, 80)

---

## 🌐 Network Issues

### Slow Downloads
**Symptoms:** Very slow recording/upload speed

**Solutions:**
1. Check internet speed: `speedtest` or similar
2. Lower recording quality
3. Record at off-peak hours
4. Check if ISP is throttling

### Telegram Rate Limiting
**Symptoms:** "Too Many Requests" errors

**Solutions:**
1. Wait 5 minutes before retrying
2. Space out commands (3-5 sec gap)
3. Don't spam buttons
4. Reduce concurrent recordings

### Firewall/VPN Issues
**Symptoms:** Can't reach jiotvapi.cdn.jio.com

**Solutions:**
```bash
# Test connectivity:
curl -I https://jiotvapi.cdn.jio.com/

# If fails, try:
# 1. Disable VPN
# 2. Check firewall rules
# 3. Use different network
```

---

## 🎬 Recording Issues

### Incomplete File
**Symptoms:** MKV file very small (< 10 MB) for 30 min recording

**Causes:**
- Stream interrupted
- FFmpeg crashed
- Insufficient disk space

**Solutions:**
1. Check disk space: `df -h`
2. Look at FFmpeg error in logs
3. Try different quality/audio
4. Try recording again

### Wrong Codec/Quality
**Symptoms:** File plays but codec is unexpected

**Solutions:**
- Codec detection is automatic from stream
- Can't force specific codec (HLS streams vary)
- Select quality before recording

### No Audio
**Symptoms:** Video plays but no sound

**Solutions:**
1. Check in quality picker - audio tracks selected?
2. Try "All Audio Tracks" option
3. Select specific language track
4. Verify stream has audio: `ffprobe stream_url`

---

## 🆘 Still Not Working?

### Collect Debug Info
```bash
# Run this and save output
python bot.py 2>&1 | tee debug.log

# Try one command and capture error
# Send debug.log to support
```

### Get Help
Contact: [@II_Madara_II](https://t.me/II_Madara_II)

Include:
- Full error message
- Python version: `python --version`
- FFmpeg version: `ffmpeg -version`
- Last 20 lines of log
- What were you trying to do?
- Has it worked before? (new error or never worked?)

---

## 📚 Additional Resources

- **JioTV API:** TS-JioTV Project
- **Pyrogram Docs:** https://docs.pyrogram.org
- **FFmpeg Docs:** https://ffmpeg.org/documentation.html
- **MongoDB:** https://docs.mongodb.com

---

**Last Updated:** April 8, 2026  
**For Bot Version:** `『𝗠𝗔𝗗𝗔𝗥𝗔』`
