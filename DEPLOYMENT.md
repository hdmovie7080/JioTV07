# 🚀 Deployment Guide

How to deploy JioTV PRO Bot to different platforms.

---

## 1️⃣ Local Machine (Development)

### Quick Start

```bash
# Clone repo
git clone https://github.com/hdmovie7080/JioTV07.git
cd JioTV07

# Install dependencies
pip install -r requirements.txt

# Configure bot
nano bot.py  # Edit API_ID, API_HASH, BOT_TOKEN, ADMIN_ID

# Run
python bot.py
```

**Output:**
```
╔══════════════════════════════════════════════════╗
║   JioTV PRO Bot  ·  『𝗠𝗔𝗗𝗔𝗥𝗔』               ║
╚══════════════════════════════════════════════════╝
   Account  : Md. Hasen Ali  (+916295958622)
   ...
```

✅ **Pros:** Simple, full control, easy debugging
❌ **Cons:** Needs to run 24/7, may not be reliable

---

## 2️⃣ Linux Server (VPS)

### Requirements
- Ubuntu 20.04+ or CentOS 8+
- 1 GB RAM (minimum)
- 10 GB storage
- SSH access

### Installation

**Step 1: Update System**
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**Step 2: Install Dependencies**
```bash
sudo apt-get install -y \
    python3.9 \
    python3-pip \
    git \
    ffmpeg \
    screen \
    curl

# Verify installations
python3 --version
ffmpeg -version
```

**Step 3: Clone & Setup**
```bash
cd /home/ubuntu
git clone https://github.com/hdmovie7080/JioTV07.git
cd JioTV07
pip3 install -r requirements.txt
```

**Step 4: Configure**
```bash
nano bot.py
# Edit: API_ID, API_HASH, BOT_TOKEN, ADMIN_ID
```

**Step 5: Create Systemd Service**

Create `/etc/systemd/system/jiotv-bot.service`:

```ini
[Unit]
Description=JioTV PRO Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/JioTV07
ExecStart=/usr/bin/python3 /home/ubuntu/JioTV07/bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl enable jiotv-bot
sudo systemctl start jiotv-bot
sudo systemctl status jiotv-bot
```

**View Logs:**
```bash
sudo journalctl -u jiotv-bot -f
```

**Stop/Restart:**
```bash
sudo systemctl restart jiotv-bot
sudo systemctl stop jiotv-bot
```

✅ **Pros:** 24/7 uptime, professional, reliable
❌ **Cons:** Costs money, needs server maintenance

---

## 3️⃣ Using Screen (Simple Persistence)

Alternative to systemd for quick deployment:

```bash
# Start bot in background
screen -S jiotv -d -m python3 bot.py

# View logs
screen -r jiotv

# Detach (Ctrl+A, then D)

# Stop
screen -S jiotv -X quit
```

---

## 4️⃣ Using Tmux (Alternative)

```bash
# Start
tmux new-session -d -s jiotv "python3 bot.py"

# Attach
tmux attach-session -t jiotv

# Kill
tmux kill-session -t jiotv
```

---

## 5️⃣ Docker Deployment

### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY bot.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p downloads temp

# Run bot
CMD ["python", "bot.py"]
```

### Build & Run

```bash
# Build image
docker build -t jiotv-bot .

# Run container
docker run -d \
  --name jiotv \
  -v $(pwd)/downloads:/app/downloads \
  -e BOT_TOKEN="YOUR_TOKEN" \
  jiotv-bot

# View logs
docker logs -f jiotv

# Stop
docker stop jiotv
docker rm jiotv
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  jiotv-bot:
    build: .
    container_name: jiotv-bot
    volumes:
      - ./downloads:/app/downloads
      - ./temp:/app/temp
    environment:
      - BOT_TOKEN=YOUR_TOKEN_HERE
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Run:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 6️⃣ Railway Deployment

### Step 1: Create Account
- Go to https://railway.app
- Sign up with GitHub

### Step 2: Connect Repository
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your JioTV07 repo

### Step 3: Configure
1. Add environment variables:
   - `BOT_TOKEN`: Your bot token
   - `API_ID`: Telegram API ID
   - `API_HASH`: Telegram API hash
   - `ADMIN_ID`: Your admin ID

2. Create `Procfile`:
```
worker: python bot.py
```

### Step 4: Deploy
- Push to GitHub
- Railway auto-deploys

**Cost:** Free tier available (limited)

---

## 7️⃣ Heroku Deployment (Older, May Have Limitations)

### Step 1: Setup
```bash
brew install heroku
heroku login
```

### Step 2: Create App
```bash
heroku create your-jiotv-bot
```

### Step 3: Configure Variables
```bash
heroku config:set BOT_TOKEN="your_token"
heroku config:set API_ID="your_api_id"
heroku config:set API_HASH="your_api_hash"
```

### Step 4: Create Procfile
```
worker: python bot.py
```

### Step 5: Deploy
```bash
git push heroku main
heroku ps:scale worker=1
heroku logs --tail
```

---

## 8️⃣ Cloud Platforms Comparison

| Platform | Cost | Ease | 24/7 | Files Storage |
|----------|------|------|------|---------------|
| **VPS (Ubuntu)** | $5-10/mo | Medium | ✅ | Local disk |
| **Docker** | Varies | Hard | ✅ | Volumes |
| **Railway** | $5/mo | Easy | ✅ | Limited |
| **AWS** | $10+/mo | Hard | ✅ | S3 bucket |
| **Google Cloud** | $20+/mo | Hard | ✅ | Cloud Storage |
| **Local** | Free | Very Easy | ❌ | Local disk |

---

## 🔐 Production Checklist

Before going live:

- [ ] Use strong MongoDB password
- [ ] Store secrets in environment variables (never hardcode)
- [ ] Enable firewall (block unnecessary ports)
- [ ] Use HTTPS where applicable
- [ ] Set up log rotation (prevent disk fill)
- [ ] Monitor disk space (for downloads)
- [ ] Set up automatic backups
- [ ] Test failover/restart procedures
- [ ] Set up monitoring/alerts
- [ ] Regular security updates

---

## 📊 Monitoring

### Check Bot Status
```bash
# See if process running
ps aux | grep bot.py

# Check memory usage
top | grep python

# Check disk space
df -h

# Check logs
tail -100 /path/to/logs
```

### Automatic Restarts

**Systemd** (already configured above):
```ini
Restart=on-failure
RestartSec=10
```

**Cron job:**
```bash
crontab -e
# Add:
*/5 * * * * pgrep -f "python bot.py" || (cd /home/ubuntu/JioTV07 && python3 bot.py &)
```

---

## 🔧 Scaling & Performance

### Multiple Bot Instances
For high load, run multiple instances:

```bash
# Instance 1
BOT_WORKER_ID=1 python3 bot.py

# Instance 2
BOT_WORKER_ID=2 python3 bot.py

# Share state via MongoDB
```

### Database Optimization
```python
# In bot.py, add indexes:
_users.create_index([("user_id", 1)], unique=True)
_users.create_index([("joined", 1)])
```

### Connection Pooling
Already configured in bot.py:
```python
r = Retry(total=3, backoff_factor=0.5)
a = HTTPAdapter(max_retries=r, pool_connections=20, pool_maxsize=20)
```

---

## 🐛 Troubleshooting Deployment

### Bot Crashes Immediately
```bash
# Check error
python3 bot.py

# Common issues:
# - Missing environment variables
# - Port already in use
# - Permissions error
```

### High Memory Usage
```python
# In bot.py, clear old sessions:
if len(_sess) > 10000:
    _sess.clear()
```

### Stuck Processes
```bash
# Kill all Python processes
pkill -f "python bot.py"

# Restart
systemctl restart jiotv-bot
```

---

## 📈 Updates & Maintenance

### Update Code
```bash
cd /home/ubuntu/JioTV07
git pull origin main
pip3 install --upgrade -r requirements.txt
systemctl restart jiotv-bot
```

### Backup Downloads
```bash
# Regular backup
tar -czf jiotv-backup-$(date +%Y%m%d).tar.gz downloads/

# Upload to S3/Google Drive
```

### Rotate Logs
```bash
# Prevent logs from filling disk
logrotate -f /etc/logrotate.d/jiotv
```

---

## 🚨 Emergency Recovery

### Restore from Backup
```bash
# If bot crashes
systemctl stop jiotv-bot

# Restore config
cp jiotv-backup.tar.gz .
tar -xzf jiotv-backup.tar.gz

# Restart
systemctl start jiotv-bot
```

### Database Recovery
```python
# If MongoDB connection lost
# Bot gracefully continues without DB
# User tracking just won't work
```

---

## 📝 Deployment Checklist

- [ ] Credentials set in environment
- [ ] FFmpeg installed on target system
- [ ] Python 3.9+ available
- [ ] Dependencies installed
- [ ] Disk space > 20GB
- [ ] Network connectivity tested
- [ ] Logs configured
- [ ] Restart policy set
- [ ] Backups configured
- [ ] Monitoring set up

---

## 🆘 Support

For deployment issues:
- [@II_Madara_II](https://t.me/II_Madara_II)
- Include: Platform, OS, Python version, error logs

---

**Last Updated:** April 8, 2026
