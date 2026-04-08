#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════
#   JioTV PRO Telegram Bot  ·  『𝗠𝗔𝗗𝗔𝗥𝗔』
#   Features: Live Recording, Catchup TV, EPG, All Audio Tracks,
#             Genre Channel Browser, Scene-Style Filenames, Auto Token Refresh
#   No login required — credentials loaded from TS-JioTV repo
# ══════════════════════════════════════════════════════════════════════════════

import os, re, sys, json, time, gzip, html, asyncio, subprocess, logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pymongo
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from pyrogram.errors import FloodWait, MessageNotModified

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))

def ist_now() -> datetime:
    return datetime.now(IST)

# ══ BOT CONFIG ════════════════════════════════════════════════════════════════
API_ID    = 20093900
API_HASH  = "314286d8af54eda517ff6f3974fd3aad"
BOT_TOKEN = "8516486280:AAHi3kgQ75gvJYJDUpSv_E8Q5DfNVK58fPs"
ADMIN_ID  = 5009476236
DB_URL    = "mongodb+srv://hdmovie7080:Q3EHYt3z5oc1Af76@cluster0.yrkrelc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME   = "Cluster0"

DOWNLOAD_DIR = "./downloads"
TEMP_DIR     = "./temp"
PAGE_SIZE    = 10
MAX_REC_SEC  = 4 * 3600   # 4 h max recording
PROGRESS_SEC = 4          # seconds between progress bar updates
RELEASE_TAG  = "『𝗠𝗔𝗗𝗔𝗥𝗔』"

# ══ JIOTV CREDENTIALS (from your TS-JioTV repo / htdocs.zip) ═════════════════
# Auth token valid until ~17 Apr 2026. Auto-refreshed via refreshToken.
_CREDS: Dict = {
    "authToken": (
        "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImF1dGhUb2tlbklkIjoi"
        "YjM2YjZjMmYtODA2Ny00NDI4LWEyNWUtZTE3NDc2YmRmY2I1IiwidXNlcklkIjoiZThkZjY"
        "xOTEtOTE1ZC00MDE0LTljOTEtN2I0ZmRjNzI2NzYwIiwidXNlclR5cGUiOiJKSU8iLCJvc"
        "yI6ImFuZHJvaWQiLCJkZXZpY2VUeXBlIjoicGhvbmUiLCJhY2Nlc3NMZXZlbCI6IjkiLCJ"
        "kZXZpY2VJZCI6ImFmNDExN2IzYjM0MjNiZTQiLCJleHRyYSI6IntcIm51bWJlclwiOlwia"
        "VdaSDg4Y1hXWjRnMzdHU1BqVjdNVjVQY0tGV2dmYldvcGVMK085eHhXU0VjOFEweGMzSXR"
        "6az1cIixcInBsYW5kZXRhaWxzXCI6e1wiUGFja2FnZUluZm9cIjpbe1wicGxhbmlkXCI6XC"
        "IxXCIsXCJzdWJzY3JpcHRpb25zdGFydFwiOjE2OTM3MzI5ODcsXCJzdWJzY3JpcHRpb25l"
        "bmRcIjoxODA3MDk5OTQ3LFwicGxhbnR5cGVcIjpcIlwiLFwiYnVzaW5lc3NUeXBlXCI6XC"
        "JqaW9cIixcIm5vdGVzXCI6XCJcIn1dfSxcImpUb2tlblwiOlwiNWM2NTQzOGRmNGJmZWMx"
        "MWZhNWViMGIxZDkzZTgyM2QuNjI3YWE5Yjk5ZWNkNjdkY2FhY2M1MWRhYjMyMzU2YmE2MD"
        "NlNmU0ZDI1NTZiYmI0MjdiYmUyN2U3NjZmNTJhMWVlMTE5ZjY3ZmZiODNkMjQzMzAwMjRl"
        "OTc0NTI2YTEyNTdjNjAxNTBjMGRiMzI0NTk2YTI3MmQzNTNlYzU1N2NhODZkZjAyYTc0NT"
        "YxMDQ5N2RmMDAzNzg0NGU5MDUzOWY2NzUwOGZhZTdmYWZlYmM4Mzk4MTY5ZDJkZWEyOTgz"
        "NjVjYTQwNTM1M2VhODFmOGRjYjU0MjQ1ZDFkNTM0ZDQxYmM1M2UxY2M5ZWYzNTk3NWFjNz"
        "UwZmVkYTcwMjNkNmYxNTQxYmFlMjExMDgzMzJkMjBlMjMxNGIxYTBkYTM3NzA4NDA0MWFl"
        "YWE2YTk2ZDkzMDYyNTU4ODQ3ZGU3ZjExN2NkZGIyZWNjYThkOTVhYjM2ODhiMzRlMGMxND"
        "kwZDg3YTc2NWE1OGQwNzc4YWZkMWY1YzI0ZWRkODk3YmFjNmI2MTM0NWFlM2JmOWE5Zjk1"
        "MDY0Y2FkOWNmYmFlN2Y5NDMwYWQ3Y2U0OWJmMzgyNmY2NjhkN2VjNDAyMWQ2NjZhNTU0OG"
        "M4ZGVjYTA2MWM4OTA4MDUwOWViYTBlZWNkYzJhM2IwY2M1OGZmODcxZDliNTc4MGY5ZjZi"
        "YzA4MGIyMzk4NjAyN2JkMzZkODUzMzQ5YWNjNzg1Yzc2N2VmM2YwODhiZGNhNmY0NTk4Nm"
        "FiMzMxMzA3MjAwNWVlNzY4NDFjM2IwM2Q2NmQ1MTFhZTIzZWIyMTFkZWNiYjNkZTA2MmFl"
        "N2FlODVjYjAyNWNiMGNjZjZkYTE4MmFmYTQxMjlhOWIxNDU2NWI5NDkyYzNlNDY4OTcyOT"
        "RjYTllMDIzMDI5MjM4OTQ0MTMxOWZiNjJjMmQyOTQ4NjY3NWFkYWRcIixcInVzZXJEZXRh"
        "aWxzXCI6XCJJay9VVTZnZTdZVEoxZjZTTTR2bHZuOGVsRlhVSUh4KzNvcDArUkluWU9FT2"
        "FxS2draFYzY25ycVd3aTQyd0V0TFR3bGZSaFVUa0Z0YW1mRFhqdE1HMmxtS01EY0h0WGo0"
        "V0xSZzhsaVcyWmdVdXhDNmYvRmNPM3kxcktMUjdEWjhwdjFmNmx0V1ZvNlYxYU5WWXZPYj"
        "ZubTYwQzBXaE44NDFWYVRsc1FzRGhiT2pkb1d1a21pZ0xjVjVEb1dBT25Kemt0UVhTQlJt"
        "aDNmeUNOZ0xFOC96YU5nb3AwU0tmd3JmTnQ4dVpiZUxEOWRqUjdmUW44Y0VHajg2TnFJS1"
        "JDb1g4eUxSYy82N1V5RjdRMjBCSU5NeEtvaTlaS3VreTI1YVYycXhuXCJ9Iiwic3Vic2Ny"
        "aWJlcklkIjoiMzEyNjcwNzgxNiIsImFwcE5hbWUiOiJSSklMX0ppb1RWIiwidmVyc2lvbi"
        "I6InYxLjEiLCJwbGF0Zm9ybSI6IiJ9LCJleHAiOjE3NzY0Mjc5NDcsImlhdCI6MTc3NTU2"
        "Mzk0N30.3-BcLoz9RoXD26pLWi9SGd79PuLParvd6yeXo9SX8zKDOwUa1dY8PWoUTJR7xg"
        "-Mpqf0FTkQFMGIdoJJ_iP7QQ"
    ),
    "ssoToken": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkRm9yIjoiSmlvVFYiLCJk"
        "ZXZpY2VJZCI6ImFmNDExN2IzYjM0MjNiZTQiLCJpYXQiOjE3NzU1NjM5NDcsInNJZCI6Il"
        "UyRnNkR1ZrWDErZ2Y0UmU0cXJ2c0M2TVNiNWhkOFBDRUtUcHFmYkkwZjg5IiwidW5pcXVl"
        "IjoiZThkZjYxOTEtOTE1ZC00MDE0LTljOTEtN2I0ZmRjNzI2NzYwIiwidXNlclR5cGUiOi"
        "KKSU8ifQ.0uqDBWxHcvJD-iqtjSBOCNLv9RZJcKxgtY3XwBCml1s"
    ),
    "refreshToken": "af939ca6-3b0c-4f5a-933f-2c24399db1f0",
    "deviceId":     "af4117b3b3423be4",
    "subscriberId": "3126707816",
    "uniqueId":     "e8df6191-915d-4014-9c91-7b4fdc726760",
    "lbCookie":     "1",
    "name":         "Md. Hasen Ali",
    "mobile":       "+916295958622",
    "refreshed_at": 0.0,
}

# ══ JioTV API URLs ════════════════════════════════════════════════════════════
JIO_PLAYBACK    = "https://jiotvapi.media.jio.com/playback/apis/v1/geturl?langId=6"
JIO_REFRESH     = "https://auth.media.jio.com/tokenservice/apis/v1/refreshtoken?langId=6"
JIO_CHANNELS    = "https://jiotvapi.cdn.jio.com/apis/v1.3/getepg/get?offset=-1&channel_id=all&langId=6"
JIO_EPG         = "https://jiotvapi.cdn.jio.com/apis/v1.3/getepg/get?offset={offset}&channel_id={ch_id}&langId=6"
JIO_APPKEY      = "NzNiMDhlYzQyNjJm"

# ══ Valid JioTV Channel IDs ═══════════════════════════════════════════════════════
# The API does NOT support channel_id=all, so we use a hardcoded list of valid channels
VALID_CHANNELS = {
    "101": "DD National", "102": "DD News", "103": "DD Bangla", "104": "DD Gujarati",
    "105": "DD Kannada", "106": "DD Marathi", "107": "DD Punjabi", "108": "DD Urdu",
    "109": "DD Bihar", "110": "DD Odia", "111": "DD Himachal",
    
    # Star channels
    "400": "Star Plus", "401": "Star Plus HD", "402": "Star Gold", "403": "Star Gold HD",
    "404": "Star Bharat", "405": "Star Jalsha", "406": "Star Jalsha HD", "407": "Star Maa",
    "408": "Star Pravah", "409": "Star Vijay", "410": "Star Vijay HD", "411": "Star Kannada",
    
    # Sony channels
    "500": "Sony SAB", "501": "Sony TV", "502": "Sony TV HD", "503": "Sony Max", 
    "504": "Sony Max HD", "505": "Sony Pal", "506": "Sony Wah", "507": "Sony Aath",
    
    # Comedy channels
    "600": "Comedy Central", "601": "SAB TV",
    
    # Kids channels  
    "700": "Disney Channel", "701": "Cartoon Network", "702": "Hungama", "703": "Nickelodeon",
    "704": "Pogo", "705": "CN Hindi",
    
    # News channels
    "800": "Republic TV", "801": "Times Now", "802": "NDTV 24x7", "803": "BBC News",
    "804": "CNN IBN", "805": "India Today TV",
    
    # Movie channels
    "811": "Zee Cinema", "812": "Zee Cinema HD", "813": "Sony Max HD", "814": "Colors Cineplex",
    "815": "Colors Cineplex HD", "816": "Cartoon Network", "817": "Hungama TV",
    "818": "Colours HD", "819": "Colors TV", "820": "Colors Infinity",
    
    # Entertainment
    "850": "Zee TV", "851": "Zee TV HD", "852": "Colors", "853": "Colors HD",
    "854": "Voot Select", "855": "Jio TV", "856": "Jio Cinema",
    
    # Sports
    "900": "Sports 18", "901": "Cricket 18", "902": "Jio Sports",
    
    # Music
    "950": "9X", "951": "9X Jalwa", "952": "B4U Kadak",
}

# ══ Language code → scene abbreviation map ════════════════════════════════════
LANG_MAP = {
    "hin":"HIN","hi":"HIN","hindi":"HIN",
    "asm":"ASM","as":"ASM","assamese":"ASM",
    "ben":"BEN","bn":"BEN","bengali":"BEN",
    "bod":"BOD","bodo":"BOD",
    "doi":"DOG","dogri":"DOG","dog":"DOG",
    "guj":"GUJ","gu":"GUJ","gujarati":"GUJ",
    "kan":"KAN","kn":"KAN","kannada":"KAN",
    "kas":"KAS","ks":"KAS","kashmiri":"KAS",
    "kok":"KON","konkani":"KON","kon":"KON",
    "mai":"MAI","maithili":"MAI",
    "mal":"MAL","ml":"MAL","malayalam":"MAL",
    "mni":"MAN","manipuri":"MAN","man":"MAN",
    "mar":"MAR","mr":"MAR","marathi":"MAR",
    "nep":"NEP","ne":"NEP","nepali":"NEP",
    "ori":"ODI","or":"ODI","odia":"ODI","odi":"ODI",
    "pan":"PUN","pa":"PUN","punjabi":"PUN","pun":"PUN",
    "san":"SAN","sa":"SAN","sanskrit":"SAN",
    "sat":"SANL","santali":"SANL","sanl":"SANL",
    "snd":"SIN","sindhi":"SIN","sin":"SIN",
    "tam":"TAM","ta":"TAM","tamil":"TAM",
    "tel":"TEL","te":"TEL","telugu":"TEL",
    "urd":"URD","ur":"URD","urdu":"URD",
    "eng":"ENG","en":"ENG","english":"ENG",
    "und":"UND","unknown":"UND","":"UND",
}

def lang_abbr(raw: str) -> str:
    return LANG_MAP.get((raw or "").strip().lower(),
                        (raw or "UND").upper()[:4])

# ══ MongoDB ═══════════════════════════════════════════════════════════════════
try:
    _mc    = pymongo.MongoClient(DB_URL)
    _db    = _mc[DB_NAME]
    _users = _db["jiotv_users"]
    _users.create_index("user_id", unique=True)
    log.info("✅ MongoDB connected")
except Exception as _me:
    _mc = _db = _users = None
    log.warning(f"⚠️  MongoDB: {_me}")

def db_add_user(uid: int, name: str = ""):
    if _users is None: return
    try:
        _users.update_one({"user_id": uid},
                          {"$set": {"user_id": uid, "name": name},
                           "$setOnInsert": {"joined": ist_now()}},
                          upsert=True)
    except Exception: pass

def db_all_users() -> List[int]:
    if _users is None: return []
    try: return [d["user_id"] for d in _users.find({}, {"user_id": 1})]
    except Exception: return []

# ══ HTTP session ══════════════════════════════════════════════════════════════
def _make_session() -> requests.Session:
    s = requests.Session()
    r = Retry(total=3, backoff_factor=0.5,
              status_forcelist=(429, 500, 502, 503, 504))
    a = HTTPAdapter(max_retries=r, pool_connections=20, pool_maxsize=20)
    s.mount("http://", a); s.mount("https://", a)
    return s

_http = _make_session()

# ══ JioTV credential helpers ══════════════════════════════════════════════════
def _jio_headers(channel_id: str = "144") -> dict:
    """Build the required JioTV API headers using stored credentials."""
    return {
        "Host":          "jiotvapi.media.jio.com",
        "Content-Type":  "application/x-www-form-urlencoded",
        "appkey":        JIO_APPKEY,
        "channel_id":    str(channel_id),
        "channelid":     str(channel_id),
        "userid":        _CREDS["subscriberId"],
        "crmid":         _CREDS["subscriberId"],
        "deviceId":      _CREDS["deviceId"],
        "devicetype":    "phone",
        "isott":         "true",
        "languageId":    "6",
        "lbcookie":      _CREDS["lbCookie"],
        "os":            "android",
        "dm":            "Xiaomi 22101316UP",
        "osversion":     "14",
        "srno":          "250918144000",
        "accesstoken":   _CREDS["authToken"],
        "ssotoken":      _CREDS["ssoToken"],
        "subscriberid":  _CREDS["subscriberId"],
        "subscriberId":  _CREDS["subscriberId"],
        "uniqueId":      _CREDS["uniqueId"],
        "usergroup":     "tvYR7NSNn7rymo3F",
        "versionCode":   "452",
        "appname":       "RJIL_JioTV",
        "User-Agent":    "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
    }

def _epg_headers() -> dict:
    return {
        "Host":               "jiotvapi.cdn.jio.com",
        "Connection":         "keep-alive",
        "User-Agent":         "okhttp/4.12.13",
        "Accept":             "*/*",
        "Accept-Encoding":    "gzip, deflate",
        "Accept-Language":    "en-US,en;q=0.9",
        "Cache-Control":      "no-cache",
        "Pragma":             "no-cache",
        "accesstoken":        _CREDS["authToken"],
        "ssotoken":           _CREDS["ssoToken"],
        "subscriberid":       _CREDS["subscriberId"],
        "deviceid":           _CREDS["deviceId"],
        "uniqueid":           _CREDS["uniqueId"],
        "versioncode":        "331",
        "os":                 "android",
        "devicetype":         "phone",
        "appname":            "RJIL_JioTV",
    }

def refresh_token() -> bool:
    """Refresh the authToken using the stored refreshToken."""
    for attempt in range(3):
        try:
            payload = json.dumps({
                "appName":      "RJIL_JioTV",
                "deviceId":     _CREDS["deviceId"],
                "refreshToken": _CREDS["refreshToken"],
            })
            headers = {
                "accesstoken": _CREDS["authToken"],
                "uniqueId":    _CREDS["uniqueId"],
                "devicetype":  "phone",
                "versionCode": "331",
                "os":          "android",
                "Content-Type":"application/json",
            }
            r    = _http.post(JIO_REFRESH, data=payload, headers=headers, timeout=15)
            data = r.json()
            if data.get("authToken"):
                _CREDS["authToken"]    = data["authToken"]
                _CREDS["ssoToken"]     = data.get("ssoToken", _CREDS["ssoToken"])
                _CREDS["refreshed_at"] = time.time()
                log.info("✅ authToken refreshed successfully")
                return True
            log.warning(f"Token refresh failed (attempt {attempt+1}/3): {data}")
        except Exception as e:
            log.error(f"refresh_token (attempt {attempt+1}/3): {e}")
            if attempt < 2:
                time.sleep(2)
            continue
    log.error("Token refresh: All attempts failed")
    return False

def ensure_token():
    """Auto-refresh token if it is older than 6800 seconds (~1.9 h)."""
    if time.time() - _CREDS.get("refreshed_at", 0) > 6800:
        refresh_token()

# ══ JioTV data helpers ════════════════════════════════════════════════════════
_ch_cache: Optional[List[dict]] = None
_ch_cache_ts: float = 0.0

def fetch_channels(force: bool = False) -> List[dict]:
    """
    Fetch all available channels.
    Note: JioTV API doesn't support channel_id=all, so we use a hardcoded list.
    """
    global _ch_cache, _ch_cache_ts
    if not force and _ch_cache and (time.time() - _ch_cache_ts < 3600):
        return _ch_cache
    ensure_token()
    
    channels = []
    
    # Build channels list from VALID_CHANNELS dict
    for ch_id, ch_name in VALID_CHANNELS.items():
        channels.append({
            "channel_id": int(ch_id),
            "channel_name": ch_name,
            "channel_id_str": ch_id,
        })
    
    _ch_cache    = channels
    _ch_cache_ts = time.time()
    log.info(f"✅ Successfully loaded {len(channels)} channels from config")
    return channels

def _ch_id(ch: dict) -> str:
    return str(ch.get("channel_id") or ch.get("channelId") or
               ch.get("id") or "")

def _ch_name(ch: dict) -> str:
    return (ch.get("channel_name") or ch.get("channelName") or
            ch.get("name") or "Unknown").strip()

def _has_catchup(ch: dict) -> bool:
    return bool(ch.get("isCatchupAvailable") or ch.get("catchup") or
                ch.get("is_catchup_available") or ch.get("isLiveAvailable"))

def group_by_genre(channels: List[dict]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    for ch in channels:
        g = (ch.get("channel_category_name") or ch.get("categoryName") or
             ch.get("category") or "Other")
        out.setdefault(g, []).append(ch)
    return dict(sorted(out.items()))

def get_stream_url(channel_id: str, stream_type: str = "Seek",
                   srno: str = "", begin: str = "", end: str = "") -> Optional[str]:
    """Get HLS stream URL for live or catchup. Retries once after token refresh."""
    ensure_token()
    payload: dict = {
        "stream_type": stream_type,
        "channel_id":  str(channel_id),
        "showtime":    "000000",
        "srno":        srno or "250918144000",
    }
    if stream_type == "Catchup":
        payload.update({"programId": srno, "begin": begin, "end": end})

    for attempt in range(2):
        try:
            r    = _http.post(JIO_PLAYBACK, headers=_jio_headers(channel_id),
                              data=payload, timeout=15)
            data = r.json()
            if data.get("code") == 200:
                return data.get("result")
            if data.get("code") in (401, 403, "401", "403"):
                if attempt == 0 and refresh_token():
                    continue          # retry with fresh token
            log.warning(f"get_stream_url ch={channel_id} type={stream_type}: {data}")
            return None
        except Exception as e:
            log.error(f"get_stream_url: {e}")
            return None
    return None

def fetch_epg(channel_id: str, offset: int = 0) -> Optional[dict]:
    """offset: 0=today, -1=yesterday, -2=2 days ago, 1=tomorrow"""
    for attempt in range(2):
        try:
            ensure_token()
            url = JIO_EPG.format(offset=offset, ch_id=channel_id)
            headers = _epg_headers()
            
            log.info(f"[DEBUG] Fetching EPG ch={channel_id} offset={offset} (attempt {attempt+1}/2)")
            log.info(f"[DEBUG] URL: {url}")
            
            r = _http.get(url, headers=headers, timeout=30, allow_redirects=True)
            
            log.info(f"[DEBUG] Response status: {r.status_code}")
            
            if r.status_code == 401 or r.status_code == 403:
                log.warning(f"[DEBUG] Auth error ({r.status_code}), refreshing...")
                if attempt == 0:
                    refresh_token()
                    time.sleep(1)
                    continue
                    
            r.raise_for_status()
            
            try:
                raw = gzip.decompress(r.content)
            except Exception:
                raw = r.content
                
            data = json.loads(raw.decode("utf-8", errors="ignore"))
            log.info(f"✅ Fetched EPG for channel {channel_id} (offset={offset}, {len(data.get('epg', []))} shows)")
            return data
            
        except Exception as e:
            log.error(f"fetch_epg ch={channel_id} offset={offset} (attempt {attempt+1}/2): {type(e).__name__}: {e}")
            if attempt == 0:
                time.sleep(1)
                
    return None

# ══ Filename builder ══════════════════════════════════════════════════════════
def _dot(s: str) -> str:
    """Convert a string to dot-separated scene format."""
    s = re.sub(r"[^\w\s.\-!+&]", "", s.strip())
    s = re.sub(r"\s+", ".", s)
    return re.sub(r"\.+", ".", s).strip(".")

def build_filename(channel: str, date_s: str, start_t: str, end_t: str,
                   quality: str, audio_langs: List[str],
                   a_codec: str = "AAC", a_ch: str = "2.0",
                   v_codec: str = "H264", ext: str = "mkv") -> str:
    """
    Builds:
    SONY.YAY!.[01-10-2025].[06.50-08.25].360p.JioTV.WEB-DL.HIN-TAM-TEL.AAC.2.0.H264-『𝗠𝗔𝗗𝗔𝗥𝗔』.mkv
    """
    ch   = _dot(channel)
    q    = quality if quality.endswith("p") else f"{quality}p"
    aud  = "-".join(lang_abbr(l) for l in audio_langs) if audio_langs else "UND"
    st   = re.sub(r"[:/ ]", ".", start_t.strip())
    et   = re.sub(r"[:/ ]", ".", end_t.strip())
    name = (f"{ch}.[{date_s}].[{st}-{et}].{q}.JioTV.WEB-DL."
            f"{aud}.{a_codec}.{a_ch}.{v_codec}-{RELEASE_TAG}.{ext}")
    return re.sub(r"\.+", ".", name)

# ══ Utils ══════════════════════════════════════════════════════════════════════
def pbar(pct: float, w: int = 14) -> str:
    pct = max(0.0, min(100.0, pct))
    f   = int(round(pct / 100.0 * w))
    return f"[{'▰'*f}{'▱'*(w-f)}]"

def fmt_bytes(b: float) -> str:
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"

def hms(s: float) -> str:
    s = max(0, int(s))
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

def parse_dur(v: str) -> int:
    pts = v.strip().split(":")
    try:
        if len(pts)==3: return int(pts[0])*3600+int(pts[1])*60+int(pts[2])
        if len(pts)==2: return int(pts[0])*60+int(pts[1])
        return int(pts[0])
    except Exception: return 0

def parse_ffmpeg_time(v: str) -> float:
    try:
        h, m, s = v.strip().split(":")
        return int(h)*3600+int(m)*60+float(s)
    except Exception: return 0.0

def height_to_q(h: int) -> str:
    for q in (2160,1080,720,480,360,240):
        if h >= q: return f"{q}p"
    return f"{h}p" if h else "best"

def codec_lbl(n: str) -> str:
    return {"h264":"H264","hevc":"H265","h265":"H265",
            "aac":"AAC","ac3":"AC3","eac3":"EAC3",
            "mp3":"MP3"}.get((n or "").lower(), (n or "UNK").upper())

def ach_lbl(c: int) -> str:
    return {0:"2.0",1:"1.0",2:"2.0"}.get(c, f"{c}.0")

def epoch_to_sec(e) -> float:
    """Handle both second-based and millisecond-based JioTV epochs."""
    try:
        v = int(e)
        return v/1000 if v > 9_999_999_999 else float(v)
    except Exception: return 0.0

# ══ ffprobe ═══════════════════════════════════════════════════════════════════
def ffprobe(url: str) -> dict:
    cmd = ["ffprobe","-v","error","-show_streams","-show_format",
           "-of","json", url]
    try:
        raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30)
        return json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        log.warning(f"ffprobe: {e}")
        return {}

def parse_probe(probe: dict) -> Tuple[List[dict], List[dict]]:
    streams = probe.get("streams", [])
    vids    = [s for s in streams if s.get("codec_type")=="video"]
    auds    = [s for s in streams if s.get("codec_type")=="audio"]

    v_opts, seen = [], set()
    for s in sorted(vids, key=lambda x: -int(x.get("height") or 0)):
        h   = int(s.get("height") or 0)
        lbl = f"{h}p" if h else f"v{s.get('index',0)}"
        if lbl in seen: continue
        seen.add(lbl)
        v_opts.append({"index": int(s.get("index") or 0), "label": lbl,
                       "height": h, "codec": codec_lbl(s.get("codec_name","h264"))})

    a_opts = []
    for s in auds:
        idx   = int(s.get("index") or 0)
        tags  = s.get("tags") or {}
        lang  = (tags.get("language") or tags.get("LANGUAGE") or "und").lower()
        title = (tags.get("title") or tags.get("NAME") or "").strip()
        codec = codec_lbl(s.get("codec_name","aac"))
        ch_n  = int(s.get("channels") or 2)
        abbr  = lang_abbr(lang)
        disp  = abbr + (f" ({title})" if title else "")
        a_opts.append({"index": idx, "lang": lang, "abbr": abbr,
                       "title": title, "display": disp,
                       "codec": codec, "channels": ch_n})
    return v_opts, a_opts

# ══ Recording ═════════════════════════════════════════════════════════════════
async def _consume_ffmpeg(stream, total_sec: int, tmp: str,
                           smsg: Message, t0: float, state: dict):
    done = 0.0
    while True:
        line = await stream.readline()
        if not line: break
        txt = line.decode(errors="ignore").strip()
        if "=" not in txt: continue
        k, _, v = txt.partition("=")
        if   k == "out_time":              done = parse_ffmpeg_time(v)
        elif k in("out_time_us","out_time_ms"):
            try: done = float(v)/1_000_000
            except Exception: pass
        elif k == "progress" and v=="end": done = float(total_sec or done)

        if total_sec > 0 and (time.time()-state.get("t",0)) >= PROGRESS_SEC:
            state["t"] = time.time()
            pct  = min(100.0, done/total_sec*100)
            sz   = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            spd  = sz/max(time.time()-t0,1e-6)/1024
            eta  = hms(max(total_sec-done,0))
            try:
                await smsg.edit(
                    f"📹 <b>Recording…</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{pbar(pct)} <b>{pct:.1f}%</b>\n"
                    f"⚡ <b>Write:</b> <code>{spd:.1f} KB/s</code>\n"
                    f"⏳ <b>ETA:</b> <code>{eta}</code>\n"
                    f"💾 <b>Size:</b> <code>{fmt_bytes(sz)}</code>",
                    parse_mode=enums.ParseMode.HTML)
            except Exception: pass

async def _upload_progress(cur, tot, smsg: Message, t0: float, state: dict):
    now = time.time()
    if cur != tot and (now-state.get("t",0)) < PROGRESS_SEC: return
    state["t"] = now
    pct = cur*100/tot if tot else 0
    spd = cur/max(now-t0,1e-6)/1024
    eta = hms((tot-cur)/max(spd*1024,1)) if spd>0 else "…"
    try:
        await smsg.edit(
            f"📤 <b>Uploading…</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{pbar(pct)} <b>{pct:.1f}%</b>\n"
            f"⚡ <b>Speed:</b> <code>{spd:.1f} KB/s</code>\n"
            f"⏳ <b>ETA:</b> <code>{eta}</code>\n"
            f"📂 <code>{fmt_bytes(cur)}</code> / <code>{fmt_bytes(tot)}</code>",
            parse_mode=enums.ParseMode.HTML)
    except Exception: pass

def make_thumb(vpath: str, tpath: str) -> bool:
    try:
        subprocess.run(["ffmpeg","-y","-ss","00:00:02","-i",vpath,
                        "-frames:v","1","-vf","scale=320:-2","-q:v","4",tpath],
                       capture_output=True, timeout=30)
        return os.path.exists(tpath) and os.path.getsize(tpath)>0
    except Exception: return False

async def do_record(
    bot_client: Client,
    chat_id: int,
    ch: dict,
    dur_str: str,
    base_name: str,
    smsg: Message,
    stream_url: Optional[str] = None,
    video_idx: Optional[int]  = None,
    audio_idxs: Optional[List[int]] = None,
    quality_label: Optional[str]    = None,
    audio_opts: Optional[List[dict]] = None,
):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    # sanitize base_name for filesystem
    safe_name = re.sub(r"[^\w\-]", "_", base_name)[:60]
    ts_path   = os.path.join(DOWNLOAD_DIR, f"{safe_name}.ts")
    mkv_path  = os.path.join(DOWNLOAD_DIR, f"{safe_name}.mkv")
    jpg_path  = os.path.join(DOWNLOAD_DIR, f"{safe_name}.jpg")
    dur_sec   = parse_dur(dur_str)
    start_dt  = ist_now()
    final_path = mkv_path

    try:
        # ── Get stream URL ─────────────────────────────────
        if not stream_url:
            stream_url = await asyncio.to_thread(
                get_stream_url, _ch_id(ch), "Seek")
        if not stream_url:
            await smsg.edit(
                "❌ <b>Could not get stream URL.</b>\n\n"
                "The token may have expired — use /refresh and try again.",
                parse_mode=enums.ParseMode.HTML)
            return

        # ── Build ffmpeg command ───────────────────────────
        cmd = ["ffmpeg","-y","-progress","pipe:1","-nostats",
               "-i", stream_url, "-t", dur_str]
        if video_idx is not None:
            cmd += ["-map", f"0:{video_idx}"]
        if audio_idxs:
            for idx in audio_idxs:
                cmd += ["-map", f"0:{idx}"]
        if video_idx is None and not audio_idxs:
            cmd += ["-map","0"]
        cmd += ["-c","copy","-ignore_unknown", ts_path]

        # ── Run ffmpeg with live progress ──────────────────
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        t0    = time.time()
        state = {"t": 0.0}
        prog  = asyncio.create_task(
            _consume_ffmpeg(proc.stdout, dur_sec, ts_path, smsg, t0, state))
        await proc.wait()
        await prog

        if not os.path.exists(ts_path) or os.path.getsize(ts_path) < 1000:
            err = (await proc.stderr.read()).decode(errors="ignore")[-500:]
            await smsg.edit(
                f"❌ <b>Recording failed.</b>\n\n"
                f"<code>{html.escape(err)}</code>",
                parse_mode=enums.ParseMode.HTML)
            return

        # ── Remux TS → MKV ────────────────────────────────
        await smsg.edit("🔄 <b>Remuxing to MKV…</b>",
                         parse_mode=enums.ParseMode.HTML)
        subprocess.run(
            ["ffmpeg","-y","-i",ts_path,"-map","0","-c","copy",mkv_path],
            capture_output=True, timeout=600)
        if os.path.exists(ts_path):
            os.remove(ts_path)

        if not os.path.exists(mkv_path) or os.path.getsize(mkv_path) < 1000:
            # fallback: rename ts to mkv
            if os.path.exists(ts_path):
                os.rename(ts_path, mkv_path)
            else:
                await smsg.edit("❌ <b>Remux failed.</b>",
                                  parse_mode=enums.ParseMode.HTML)
                return

        # ── Probe final file for metadata ──────────────────
        meta    = ffprobe(mkv_path)
        mstrs   = meta.get("streams", [])
        v_s     = next((s for s in mstrs if s.get("codec_type")=="video"), {})
        a_ss    = [s for s in mstrs if s.get("codec_type")=="audio"]
        v_dur   = int(float((meta.get("format") or {}).get("duration") or dur_sec))
        v_h     = int(v_s.get("height") or 0)
        v_w     = int(v_s.get("width")  or 0)
        v_codec = codec_lbl(v_s.get("codec_name","h264"))
        a_codec = codec_lbl(a_ss[0].get("codec_name","aac")) if a_ss else "AAC"
        a_ch_n  = int(a_ss[0].get("channels",2)) if a_ss else 2
        qlbl    = quality_label or height_to_q(v_h)

        # ── Determine audio language labels ────────────────
        if audio_opts and audio_idxs:
            idx2lang = {a["index"]: a["lang"] for a in audio_opts}
            langs    = [idx2lang.get(i,"und") for i in audio_idxs]
        else:
            langs = []
            for s in a_ss:
                tags = s.get("tags") or {}
                langs.append(tags.get("language") or
                              tags.get("LANGUAGE") or "und")

        end_dt  = start_dt + timedelta(seconds=v_dur)
        date_s  = start_dt.strftime("%d-%m-%Y")
        st_s    = start_dt.strftime("%H.%M")
        et_s    = end_dt.strftime("%H.%M")
        fname   = build_filename(
            _ch_name(ch), date_s, st_s, et_s, qlbl,
            langs, a_codec, ach_lbl(a_ch_n), v_codec, "mkv")
        final_path = os.path.join(DOWNLOAD_DIR, fname)
        try:
            os.rename(mkv_path, final_path)
        except Exception:
            final_path = mkv_path
            fname = os.path.basename(mkv_path)

        thumb_ok = make_thumb(final_path, jpg_path)
        fs       = os.path.getsize(final_path)
        aud_tag  = "-".join(lang_abbr(l) for l in langs) or "UND"

        # ── Upload ─────────────────────────────────────────
        await smsg.edit("📤 <b>Uploading…</b>",
                         parse_mode=enums.ParseMode.HTML)
        up_t0   = time.time()
        up_state = {"t": 0.0}
        caption = (
            f"<code>{html.escape(fname)}</code>\n\n"
            f"📺 <b>Quality:</b> <code>{qlbl}</code>\n"
            f"🔊 <b>Audio:</b> <code>{aud_tag}</code>\n"
            f"🎞 <b>Codec:</b> <code>{v_codec} · {a_codec} {ach_lbl(a_ch_n)}</code>\n"
            f"💾 <b>Size:</b> <code>{fmt_bytes(fs)}</code>\n"
            f"⏱ <b>Duration:</b> <code>{hms(v_dur)}</code>"
        )
        try:
            await bot_client.send_video(
                chat_id=chat_id, video=final_path,
                thumb=jpg_path if thumb_ok else None,
                duration=v_dur, width=v_w, height=v_h,
                supports_streaming=True,
                caption=caption, parse_mode=enums.ParseMode.HTML,
                progress=_upload_progress,
                progress_args=(smsg, up_t0, up_state))
        except Exception:
            # Fallback to document if video send fails
            await bot_client.send_document(
                chat_id=chat_id, document=final_path,
                thumb=jpg_path if thumb_ok else None,
                caption=caption, parse_mode=enums.ParseMode.HTML)

    except asyncio.CancelledError:
        await smsg.edit("🚫 <b>Recording cancelled.</b>",
                         parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        log.exception(f"do_record error: {e}")
        try:
            await smsg.edit(
                f"❌ <b>Error:</b>\n<code>{html.escape(str(e)[:300])}</code>",
                parse_mode=enums.ParseMode.HTML)
        except Exception: pass
    finally:
        # Clean up temp files
        for fp in [ts_path, mkv_path, final_path, jpg_path]:
            if fp and os.path.exists(fp):
                try: os.remove(fp)
                except Exception: pass
        _active_rec.pop(chat_id, None)
        try: await smsg.delete()
        except Exception: pass

# ══ Pyrogram bot ══════════════════════════════════════════════════════════════
bot = Client("jiotv_madara",
             api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

_active_rec: Dict[int, asyncio.Task] = {}   # chat_id → recording task
_sess:       Dict[int, dict]         = {}   # msg_id  → session data

# ── Helper: build the quality+audio picker message text ──
def _picker_text(cname: str, quality: str, a_opts: List[dict]) -> str:
    langs = "-".join(a["abbr"] for a in a_opts[:8]) or "?"
    return (
        f"🎛️ <b>Quality &amp; Audio Picker</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📺 <b>Channel:</b> <code>{html.escape(cname)}</code>\n"
        f"🎞 <b>Quality:</b> <code>{html.escape(quality)}</code>\n"
        f"🔊 <b>Audio:</b> <code>{langs}</code>"
    )

def _picker_kb(mid: int) -> InlineKeyboardMarkup:
    d      = _sess.get(mid, {})
    v_opts = d.get("v_opts", [])
    a_opts = d.get("a_opts", [])
    sel_v  = d.get("sel_vid")
    sel_a  = set(d.get("sel_aud", []))
    rows   = []

    # Quality buttons
    if v_opts:
        rows.append([InlineKeyboardButton("── 🎞 Quality ──", callback_data="noop")])
        row = []
        for v in v_opts[:6]:
            tick = "✅ " if sel_v == v["index"] else ""
            row.append(InlineKeyboardButton(
                f"{tick}{v['label']}",
                callback_data=f"qsel:{mid}:{v['index']}"))
            if len(row) == 3: rows.append(row); row = []
        if row: rows.append(row)

    # Audio buttons
    if a_opts:
        rows.append([InlineKeyboardButton("── 🔊 Audio Tracks ──", callback_data="noop")])
        all_tick = "✅ " if d.get("all_audio") else ""
        rows.append([InlineKeyboardButton(f"{all_tick}All Audio Tracks",
                                           callback_data=f"aall:{mid}")])
        for a in a_opts[:12]:
            tick = "✅ " if (a["index"] in sel_a and not d.get("all_audio")) else ""
            lbl  = a.get("title") or a["abbr"]
            rows.append([InlineKeyboardButton(
                f"{tick}{lbl}",
                callback_data=f"asel:{mid}:{a['index']}")])

    rows.append([
        InlineKeyboardButton("▶️ Start Recording", callback_data=f"rstart:{mid}"),
        InlineKeyboardButton("❌ Cancel",           callback_data=f"rcancel:{mid}"),
    ])
    return InlineKeyboardMarkup(rows)

def _programs_kb(mid: int, programs: List[dict], page: int) -> InlineKeyboardMarkup:
    s    = page * PAGE_SIZE
    e    = min(s + PAGE_SIZE, len(programs))
    rows = []
    for i in range(s, e):
        p     = programs[i]
        title = (p.get("showname") or p.get("title") or "Unknown")[:35]
        start = p.get("startEpoch") or p.get("start") or 0
        try:
            se  = epoch_to_sec(start)
            t_s = datetime.fromtimestamp(se, IST).strftime("%H:%M") if se else ""
        except Exception: t_s = ""
        lbl = f"{'⏱ ' if t_s else '📌 '}{(t_s+' ') if t_s else ''}{title}"
        rows.append([InlineKeyboardButton(lbl, callback_data=f"ppick:{mid}:{i}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"ppage:{mid}:{page-1}"))
    if e < len(programs):
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"ppage:{mid}:{page+1}"))
    if nav: rows.append(nav)
    rows.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}")])
    return InlineKeyboardMarkup(rows)

# ══ Commands ══════════════════════════════════════════════════════════════════

@bot.on_message(filters.command("start") & filters.private)
async def cmd_start(client, message: Message):
    uid = message.from_user.id
    db_add_user(uid, message.from_user.first_name or "")
    await message.reply(
        f"📺 <b>JioTV PRO Bot — {RELEASE_TAG}</b>\n\n"
        f"Record live JioTV channels, download catchup TV,\n"
        f"browse EPG guide — everything with all audio tracks!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📋 Commands:</b>\n"
        f"📺 /channels — Browse channels by genre\n"
        f"🔍 /search &lt;name&gt; — Find channels\n"
        f"📋 /list — All channels with IDs\n"
        f"⏺ /record &lt;id&gt; &lt;HH:MM:SS&gt; — Record live TV\n"
        f"📼 /catchup — Catchup TV browser\n"
        f"📅 /crip -c &lt;id&gt; &lt;offset&gt; — Direct catchup\n"
        f"📡 /epg &lt;id or name&gt; — TV schedule / guide\n"
        f"❌ /cancel — Stop active recording\n"
        f"🔄 /refresh — Renew auth token\n"
        f"📊 /status — Account & token status\n"
        f"❓ /help — Full command reference\n\n"
        f"<i>Support: @II_Madara_II</i>",
        parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("help") & filters.private)
async def cmd_help(client, message: Message):
    await message.reply(
        f"❓ <b>JioTV PRO — Full Command Reference</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📺 Channel Browser:</b>\n"
        f"/channels — Interactive genre-divided browser\n"
        f"/list — Full list with IDs  (📼 = catchup available)\n"
        f"/search &lt;query&gt; — Search by channel name\n\n"
        f"<b>⏺ Live Recording:</b>\n"
        f"<code>/record &lt;channel_id&gt; &lt;HH:MM:SS&gt;</code>\n"
        f"  Probes stream → quality &amp; audio picker → records\n"
        f"  All audio tracks selected by default\n"
        f"  Example: <code>/record 144 00:30:00</code>\n\n"
        f"<b>📼 Catchup TV:</b>\n"
        f"/catchup — Genre browser for catchup channels\n"
        f"<code>/crip -c &lt;channel_id&gt; &lt;offset&gt;</code>\n"
        f"  offset: 0=today  -1=yesterday  -2=two days ago\n"
        f"  Example: <code>/crip -c 144 -1</code>\n\n"
        f"<b>📡 EPG / TV Guide:</b>\n"
        f"<code>/epg &lt;channel_id or name&gt;</code>\n"
        f"  Shows today's schedule with 🔴 LIVE indicator\n"
        f"  Example: <code>/epg 144</code>  or  <code>/epg star sports</code>\n\n"
        f"<b>⚙️ Utility:</b>\n"
        f"/cancel — Cancel active recording\n"
        f"/refresh — Force-refresh auth token\n"
        f"/status — Show account &amp; token expiry\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>📁 Output filename format:</b>\n"
        f"<code>CHANNEL.[DD-MM-YYYY].[HH.MM-HH.MM].QUALp"
        f".JioTV.WEB-DL.LANGS.AAC.2.0.H264-{RELEASE_TAG}.mkv</code>",
        parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("status") & filters.private)
async def cmd_status(client, message: Message):
    import base64 as b64
    try:
        parts   = _CREDS["authToken"].split(".")
        payload = json.loads(b64.b64decode(parts[1]+"==").decode())
        exp     = payload.get("exp", 0)
        exp_dt  = datetime.fromtimestamp(exp, IST).strftime("%d %b %Y %H:%M IST")
        valid   = "✅ Valid" if exp > time.time() else "❌ Expired"
    except Exception:
        exp_dt = "Unknown"; valid = "⚠️ Unknown"
    rec_count = len(_active_rec)
    await message.reply(
        f"📊 <b>JioTV Account Status</b>\n\n"
        f"👤 <b>Name:</b> {html.escape(_CREDS['name'])}\n"
        f"📱 <b>Mobile:</b> <code>{_CREDS['mobile']}</code>\n"
        f"🆔 <b>Subscriber ID:</b> <code>{_CREDS['subscriberId']}</code>\n"
        f"📟 <b>Device ID:</b> <code>{_CREDS['deviceId']}</code>\n\n"
        f"🔑 <b>Auth Token:</b> {valid}\n"
        f"⏰ <b>Expires:</b> {exp_dt}\n\n"
        f"🔴 <b>Active recordings:</b> {rec_count}\n\n"
        f"Use /refresh to manually renew the token.",
        parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("refresh") & filters.private)
async def cmd_refresh(client, message: Message):
    msg = await message.reply("🔄 <b>Refreshing auth token…</b>",
                               parse_mode=enums.ParseMode.HTML)
    ok = await asyncio.to_thread(refresh_token)
    if ok:
        await msg.edit("✅ <b>Token refreshed successfully!</b>",
                        parse_mode=enums.ParseMode.HTML)
    else:
        await msg.edit(
            "❌ <b>Token refresh failed.</b>\n\n"
            "The refresh token may have expired.\n"
            "You may need to update credentials in the bot.",
            parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("channels") & filters.private)
async def cmd_channels(client, message: Message):
    db_add_user(message.from_user.id, message.from_user.first_name or "")
    msg = await message.reply("⏳ <b>Loading channels…</b>",
                               parse_mode=enums.ParseMode.HTML)
    chs = await asyncio.to_thread(fetch_channels)
    if not chs:
        await msg.edit("❌ <b>Could not fetch channels.</b>\nTry /refresh first.",
                        parse_mode=enums.ParseMode.HTML)
        return
    genres = group_by_genre(chs)
    mid    = msg.id
    # Store compact data: {genre_name: [{id, name, cu}, ...]}
    _sess[mid] = {
        "type": "genre_list",
        "genres": {
            g: [{"id": _ch_id(c), "name": _ch_name(c), "cu": _has_catchup(c)}
                for c in cs]
            for g, cs in genres.items()
        },
    }
    btns = [[InlineKeyboardButton(f"📺 {g} ({len(cs)})",
                                   callback_data=f"genre:{mid}:{g[:28]}")]
            for g, cs in list(genres.items())[:20]]
    btns.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}")])
    await msg.edit(
        f"📺 <b>JioTV Channels</b>\n"
        f"<b>{len(chs)}</b> channels in <b>{len(genres)}</b> genres\n\n"
        f"Select a genre:",
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("list") & filters.private)
async def cmd_list(client, message: Message):
    db_add_user(message.from_user.id, message.from_user.first_name or "")
    msg  = await message.reply("⏳ <b>Loading…</b>", parse_mode=enums.ParseMode.HTML)
    chs  = await asyncio.to_thread(fetch_channels)
    gens = group_by_genre(chs)
    lines= ["📋 <b>JioTV Channel List</b>  (📼 = catchup)\n"]
    for g, cs in gens.items():
        lines.append(f"\n<b>── {html.escape(g)} ──</b>")
        for c in cs:
            cu = " 📼" if _has_catchup(c) else ""
            lines.append(f"  <code>{_ch_id(c)}</code> — {html.escape(_ch_name(c))}{cu}")
    text = "\n".join(lines)
    if len(text) > 4000:
        os.makedirs(TEMP_DIR, exist_ok=True)
        fpath = os.path.join(TEMP_DIR, "jiotv_channels.txt")
        with open(fpath,"w",encoding="utf-8") as f:
            f.write(re.sub(r"<[^>]+>","",text))
        await msg.delete()
        await message.reply_document(
            fpath,
            caption="📋 <b>JioTV Channel List</b>  (📼 = catchup available)",
            parse_mode=enums.ParseMode.HTML)
        os.remove(fpath)
    else:
        await msg.edit(text, parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("search") & filters.private)
async def cmd_search(client, message: Message):
    args = message.command
    if len(args) < 2:
        await message.reply("❌ Usage: <code>/search &lt;channel name&gt;</code>",
                             parse_mode=enums.ParseMode.HTML)
        return
    query = " ".join(args[1:]).strip().lower()
    msg   = await message.reply(f"🔍 Searching <b>{html.escape(query)}</b>…",
                                  parse_mode=enums.ParseMode.HTML)
    chs   = await asyncio.to_thread(fetch_channels)
    hits  = [c for c in chs if query in _ch_name(c).lower()]
    if not hits:
        await msg.edit(f"❌ No results for <b>{html.escape(query)}</b>.",
                        parse_mode=enums.ParseMode.HTML)
        return
    lines = [f"🔍 <b>Results for: {html.escape(query)}</b>\n"]
    for c in hits[:30]:
        cu = " 📼" if _has_catchup(c) else ""
        lines.append(f"  <code>{_ch_id(c)}</code> — {html.escape(_ch_name(c))}{cu}")
    await msg.edit("\n".join(lines), parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("record") & filters.private)
async def cmd_record(client, message: Message):
    db_add_user(message.from_user.id, message.from_user.first_name or "")
    args = message.command
    if len(args) < 3:
        await message.reply(
            "❌ <b>Usage:</b> <code>/record &lt;channel_id&gt; &lt;HH:MM:SS&gt;</code>\n\n"
            "Example: <code>/record 144 00:30:00</code>\n"
            "Use /list or /search to find channel IDs.",
            parse_mode=enums.ParseMode.HTML)
        return
    uid     = message.from_user.id
    cid_arg = args[1].strip()
    dur_arg = args[2].strip()
    dur_sec = parse_dur(dur_arg)
    if dur_sec <= 0:
        await message.reply("❌ Invalid duration. Use <code>HH:MM:SS</code> format.",
                             parse_mode=enums.ParseMode.HTML)
        return
    if dur_sec > MAX_REC_SEC:
        await message.reply(f"❌ Maximum recording duration is {MAX_REC_SEC//3600} hours.",
                             parse_mode=enums.ParseMode.HTML)
        return
    if uid in _active_rec:
        await message.reply(
            "⚠️ <b>You already have an active recording!</b>\n"
            "Use /cancel to stop it first.",
            parse_mode=enums.ParseMode.HTML)
        return

    chs = await asyncio.to_thread(fetch_channels)
    ch  = next((c for c in chs if _ch_id(c) == cid_arg), None)
    if not ch:
        await message.reply(
            f"❌ Channel ID <code>{html.escape(cid_arg)}</code> not found.\n"
            f"Use /list or /search to find the correct ID.",
            parse_mode=enums.ParseMode.HTML)
        return

    msg = await message.reply("⏳ <b>Probing stream quality &amp; audio tracks…</b>",
                               parse_mode=enums.ParseMode.HTML)
    url = await asyncio.to_thread(get_stream_url, cid_arg, "Seek")
    if not url:
        await msg.edit(
            "❌ <b>Could not get stream URL.</b>\nTry /refresh then retry.",
            parse_mode=enums.ParseMode.HTML)
        return

    probe        = await asyncio.to_thread(ffprobe, url)
    v_opts, a_opts = parse_probe(probe)

    mid = msg.id
    _sess[mid] = {
        "type":       "record",
        "ch":         ch,
        "dur":        dur_arg,
        "url":        url,
        "v_opts":     v_opts,
        "a_opts":     a_opts,
        "sel_vid":    v_opts[0]["index"] if v_opts else None,
        "sel_aud":    [a["index"] for a in a_opts],   # all by default
        "quality":    v_opts[0]["label"] if v_opts else "best",
        "all_audio":  True,
        "uid":        uid,
    }
    await msg.edit(
        _picker_text(_ch_name(ch),
                     v_opts[0]["label"] if v_opts else "best",
                     a_opts),
        reply_markup=_picker_kb(mid),
        parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("cancel") & filters.private)
async def cmd_cancel(client, message: Message):
    uid = message.from_user.id
    t   = _active_rec.pop(uid, None)
    if t and not t.done():
        t.cancel()
        await message.reply("🚫 <b>Recording cancelled.</b>",
                             parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply("ℹ️ No active recording to cancel.",
                             parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("epg") & filters.private)
async def cmd_epg(client, message: Message):
    args = message.command
    if len(args) < 2:
        await message.reply(
            "❌ <b>Usage:</b> <code>/epg &lt;channel_id or name&gt;</code>\n\n"
            "Examples:\n"
            "<code>/epg 144</code>\n"
            "<code>/epg star sports</code>",
            parse_mode=enums.ParseMode.HTML)
        return
    query = " ".join(args[1:]).strip()
    msg   = await message.reply("⏳ <b>Fetching TV guide…</b>",
                                  parse_mode=enums.ParseMode.HTML)
    chs = await asyncio.to_thread(fetch_channels)
    ch  = None
    if query.isdigit():
        ch = next((c for c in chs if _ch_id(c) == query), None)
    if not ch:
        hits = [c for c in chs if query.lower() in _ch_name(c).lower()]
        if hits: ch = hits[0]
    if not ch:
        await msg.edit(f"❌ Channel <b>{html.escape(query)}</b> not found. "
                        f"Try /search.", parse_mode=enums.ParseMode.HTML)
        return

    cid   = _ch_id(ch)
    cname = _ch_name(ch)
    epg   = await asyncio.to_thread(fetch_epg, cid, 0)
    if not epg:
        await msg.edit(f"❌ No EPG data for <b>{html.escape(cname)}</b>.",
                        parse_mode=enums.ParseMode.HTML)
        return

    progs = (epg.get("epg") or epg.get("programs") or
             epg.get("result") or [])
    if not progs:
        await msg.edit(f"ℹ️ No programs available for <b>{html.escape(cname)}</b>.",
                        parse_mode=enums.ParseMode.HTML)
        return

    date_s = (epg.get("serverDate","")[:10] or
               ist_now().strftime("%d-%m-%Y"))
    now_ts = time.time()
    lines  = [f"📡 <b>{html.escape(cname)}</b> — TV Guide\n"
               f"📅 {date_s}\n━━━━━━━━━━━━━━━━━━━━"]
    for p in progs[:20]:
        title = html.escape(
            (p.get("showname") or p.get("title") or "Unknown").strip())
        se  = epoch_to_sec(p.get("startEpoch") or p.get("start") or 0)
        ee  = epoch_to_sec(p.get("endEpoch")   or p.get("end")   or 0)
        try:
            st = datetime.fromtimestamp(se, IST).strftime("%H:%M") if se else "?"
            et = datetime.fromtimestamp(ee, IST).strftime("%H:%M") if ee else "?"
        except Exception: st = "?"; et = "?"
        live = " 🔴 <b>LIVE</b>" if (se and ee and se <= now_ts <= ee) else ""
        lines.append(f"<code>{st}–{et}</code>  {title}{live}")

    await msg.edit("\n".join(lines), parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("catchup") & filters.private)
async def cmd_catchup(client, message: Message):
    db_add_user(message.from_user.id, message.from_user.first_name or "")
    msg  = await message.reply("⏳ <b>Loading catchup channels…</b>",
                                parse_mode=enums.ParseMode.HTML)
    chs  = await asyncio.to_thread(fetch_channels)
    cu   = [c for c in chs if _has_catchup(c)]
    if not cu:
        await msg.edit("❌ No catchup channels found.",
                        parse_mode=enums.ParseMode.HTML)
        return
    genres = group_by_genre(cu)
    mid    = msg.id
    _sess[mid] = {
        "type": "cu_genres",
        "genres": {
            g: [{"id": _ch_id(c), "name": _ch_name(c)} for c in cs]
            for g, cs in genres.items()
        },
    }
    btns = [[InlineKeyboardButton(f"📼 {g} ({len(cs)})",
                                   callback_data=f"cu_genre:{mid}:{g[:28]}")]
            for g, cs in list(genres.items())[:20]]
    btns.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}")])
    await msg.edit(
        f"📼 <b>JioTV Catchup TV</b>\n"
        f"<b>{len(cu)}</b> channels in <b>{len(genres)}</b> genres\n\n"
        f"Select a genre:",
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("crip") & filters.private)
async def cmd_crip(client, message: Message):
    """
    /crip -c <channel_id> <date_offset>
    Shows all catchup programs for that date; user taps one to download.
    """
    db_add_user(message.from_user.id, message.from_user.first_name or "")
    parts   = message.text.split()
    cid_arg = None; offset = 0
    try:
        if "-c" in parts:
            ci      = parts.index("-c")
            cid_arg = parts[ci + 1]
            if len(parts) > ci + 2:
                offset = int(parts[ci + 2])
    except Exception: pass

    if not cid_arg:
        await message.reply(
            "❌ <b>Usage:</b> <code>/crip -c &lt;channel_id&gt; &lt;date_offset&gt;</code>\n\n"
            "Offset: <code>0</code>=today  <code>-1</code>=yesterday  "
            "<code>-2</code>=two days ago\n\n"
            "Example: <code>/crip -c 144 -1</code>",
            parse_mode=enums.ParseMode.HTML)
        return

    msg  = await message.reply("⏳ <b>Fetching catchup programs…</b>",
                                parse_mode=enums.ParseMode.HTML)
    chs  = await asyncio.to_thread(fetch_channels)
    ch   = next((c for c in chs if _ch_id(c) == cid_arg), None)
    if not ch:
        await msg.edit(
            f"❌ Channel <code>{html.escape(cid_arg)}</code> not found. Use /list.",
            parse_mode=enums.ParseMode.HTML)
        return
    if not _has_catchup(ch):
        await msg.edit(
            f"❌ <b>{html.escape(_ch_name(ch))}</b> does not support catchup.",
            parse_mode=enums.ParseMode.HTML)
        return

    epg = await asyncio.to_thread(fetch_epg, cid_arg, offset)
    if not epg:
        await msg.edit("❌ No catchup data returned.",
                        parse_mode=enums.ParseMode.HTML)
        return
    progs = (epg.get("epg") or epg.get("programs") or
             epg.get("result") or [])
    if not progs:
        await msg.edit("ℹ️ No programs found for this date.",
                        parse_mode=enums.ParseMode.HTML)
        return

    date_s = epg.get("serverDate","")[:10] or "Today"
    mid    = msg.id
    _sess[mid] = {
        "type":     "crip_programs",
        "programs": progs,
        "ch":       ch,
        "date_s":   date_s,
        "uid":      message.from_user.id,
        "page":     0,
    }
    await msg.edit(
        f"📼 <b>{html.escape(_ch_name(ch))}</b>\n"
        f"📅 {date_s}  —  {len(progs)} programs\n\n"
        f"Tap a program to download:",
        reply_markup=_programs_kb(mid, progs, 0),
        parse_mode=enums.ParseMode.HTML)

# ══ Admin ═════════════════════════════════════════════════════════════════════
@bot.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def cmd_users(client, message: Message):
    uids = db_all_users()
    await message.reply(f"👥 <b>Total Users:</b> <code>{len(uids)}</code>",
                         parse_mode=enums.ParseMode.HTML)

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def cmd_broadcast(client, message: Message):
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        await message.reply("❌ <code>/broadcast &lt;message&gt;</code>",
                             parse_mode=enums.ParseMode.HTML)
        return
    text  = parts[1]
    uids  = db_all_users()
    smsg  = await message.reply(f"📢 Broadcasting to {len(uids)} users…")
    sent = fail = 0
    for uid in uids:
        try:
            await client.send_message(uid, text, parse_mode=enums.ParseMode.HTML)
            sent += 1
        except Exception: fail += 1
        await asyncio.sleep(0.05)
    await smsg.edit(f"✅ Sent: <b>{sent}</b>  ❌ Failed: <b>{fail}</b>",
                     parse_mode=enums.ParseMode.HTML)

# ══ Callback query router ══════════════════════════════════════════════════════
@bot.on_callback_query()
async def on_cb(client, cb: CallbackQuery):
    data = cb.data or ""
    uid  = cb.from_user.id

    # ── noop ─────────────────────────────────────────────
    if data == "noop":
        return await cb.answer()

    # ── close ────────────────────────────────────────────
    if data.startswith("close:"):
        mid = int(data.split(":")[1])
        _sess.pop(mid, None)
        try: await cb.message.edit("❎ Closed.")
        except Exception: pass
        return await cb.answer()

    if data == "close_inline":
        try: await cb.message.delete()
        except Exception: pass
        return await cb.answer()

    # ─────────────────────────────────────────────────────
    # LIVE CHANNEL GENRE BROWSER
    # ─────────────────────────────────────────────────────
    if data.startswith("genre:"):
        _, mid_s, genre = data.split(":", 2)
        mid  = int(mid_s)
        d    = _sess.get(mid, {})
        chs  = d.get("genres", {}).get(genre, [])
        if not chs:
            return await cb.answer("Genre not found.", show_alert=True)
        btns = []
        for c in chs[:PAGE_SIZE]:
            cu  = " 📼" if c.get("cu") else ""
            btns.append([InlineKeyboardButton(
                f"{c['name']}{cu}  (ID:{c['id']})",
                callback_data=f"ch_info:{c['id']}")])
        btns.append([
            InlineKeyboardButton("⬅️ Back",  callback_data=f"genres_back:{mid}"),
            InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}"),
        ])
        await cb.message.edit(
            f"📺 <b>{html.escape(genre)}</b> — {len(chs)} channels:",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML)
        return await cb.answer()

    if data.startswith("genres_back:"):
        mid    = int(data.split(":")[1])
        d      = _sess.get(mid, {})
        genres = d.get("genres", {})
        btns   = [[InlineKeyboardButton(f"📺 {g} ({len(cs)})",
                                         callback_data=f"genre:{mid}:{g[:28]}")]
                  for g, cs in list(genres.items())[:20]]
        btns.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}")])
        await cb.message.edit(
            "📺 <b>JioTV Channels</b>\n\nSelect a genre:",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML)
        return await cb.answer()

    if data.startswith("ch_info:"):
        cid_arg  = data.split(":")[1]
        chs      = await asyncio.to_thread(fetch_channels)
        ch       = next((c for c in chs if _ch_id(c) == cid_arg), None)
        if not ch:
            return await cb.answer("Channel not found.", show_alert=True)
        cname = html.escape(_ch_name(ch))
        cat   = html.escape(ch.get("channel_category_name") or
                              ch.get("categoryName") or ch.get("category") or "")
        cu    = "✅ Yes" if _has_catchup(ch) else "❌ No"
        btns  = [
            [InlineKeyboardButton("⏺ 30 min",   callback_data=f"qrec:{cid_arg}:00:30:00"),
             InlineKeyboardButton("⏺ 1 hour",   callback_data=f"qrec:{cid_arg}:01:00:00"),
             InlineKeyboardButton("⏺ 2 hours",  callback_data=f"qrec:{cid_arg}:02:00:00")],
            [InlineKeyboardButton("📡 EPG",      callback_data=f"epg_ch:{cid_arg}"),
             InlineKeyboardButton("❌ Close",    callback_data="close_inline")],
        ]
        await cb.message.edit(
            f"📺 <b>{cname}</b>\n\n"
            f"🆔 <b>ID:</b> <code>{cid_arg}</code>\n"
            f"🏷 <b>Category:</b> {cat}\n"
            f"📼 <b>Catchup:</b> {cu}\n\n"
            f"Custom: <code>/record {cid_arg} 00:30:00</code>",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML)
        return await cb.answer()

    # ── Quick record buttons ──────────────────────────────
    if data.startswith("qrec:"):
        parts   = data.split(":")
        cid_arg = parts[1]
        dur_arg = ":".join(parts[2:])
        if uid in _active_rec:
            return await cb.answer("Already recording! /cancel first.",
                                    show_alert=True)
        await cb.answer("⏳ Starting…")
        chs = await asyncio.to_thread(fetch_channels)
        ch  = next((c for c in chs if _ch_id(c) == cid_arg), None)
        if not ch:
            return await cb.message.reply("❌ Channel not found.",
                                           parse_mode=enums.ParseMode.HTML)
        smsg  = await cb.message.reply("⏳ <b>Probing stream…</b>",
                                        parse_mode=enums.ParseMode.HTML)
        url   = await asyncio.to_thread(get_stream_url, cid_arg, "Seek")
        if not url:
            return await smsg.edit("❌ Could not get stream URL.",
                                    parse_mode=enums.ParseMode.HTML)
        probe        = await asyncio.to_thread(ffprobe, url)
        v_opts, a_opts = parse_probe(probe)
        t = asyncio.create_task(do_record(
            client, cb.message.chat.id, ch, dur_arg, cid_arg,
            smsg, url,
            v_opts[0]["index"] if v_opts else None,
            [a["index"] for a in a_opts],
            v_opts[0]["label"] if v_opts else "best",
            a_opts))
        _active_rec[uid] = t
        return

    # ── EPG inline ───────────────────────────────────────
    if data.startswith("epg_ch:"):
        cid_arg = data.split(":")[1]
        await cb.answer("Fetching EPG…")
        chs   = await asyncio.to_thread(fetch_channels)
        ch    = next((c for c in chs if _ch_id(c) == cid_arg), None)
        cname = _ch_name(ch) if ch else cid_arg
        epg   = await asyncio.to_thread(fetch_epg, cid_arg, 0)
        if not epg:
            return await cb.message.reply(
                f"❌ No EPG for <b>{html.escape(cname)}</b>.",
                parse_mode=enums.ParseMode.HTML)
        progs  = (epg.get("epg") or epg.get("programs") or
                  epg.get("result") or [])
        date_s = epg.get("serverDate","")[:10] or ist_now().strftime("%d-%m-%Y")
        now_ts = time.time()
        lines  = [f"📡 <b>{html.escape(cname)}</b>\n"
                   f"📅 {date_s}\n━━━━━━━━━━━━━━━━━━━━"]
        for p in progs[:15]:
            title = html.escape(
                (p.get("showname") or p.get("title") or "?").strip())
            se = epoch_to_sec(p.get("startEpoch") or p.get("start") or 0)
            ee = epoch_to_sec(p.get("endEpoch")   or p.get("end")   or 0)
            try:
                st = datetime.fromtimestamp(se, IST).strftime("%H:%M") if se else "?"
                et = datetime.fromtimestamp(ee, IST).strftime("%H:%M") if ee else "?"
            except Exception: st = "?"; et = "?"
            lv = " 🔴" if (se and ee and se <= now_ts <= ee) else ""
            lines.append(f"<code>{st}–{et}</code>  {title}{lv}")
        await cb.message.reply("\n".join(lines), parse_mode=enums.ParseMode.HTML)
        return

    # ─────────────────────────────────────────────────────
    # CATCHUP GENRE BROWSER
    # ─────────────────────────────────────────────────────
    if data.startswith("cu_genre:"):
        _, mid_s, genre = data.split(":", 2)
        mid  = int(mid_s)
        d    = _sess.get(mid, {})
        chs  = d.get("genres", {}).get(genre, [])
        if not chs:
            return await cb.answer("Genre not found.", show_alert=True)
        btns = [[InlineKeyboardButton(f"📼 {c['name']}  (ID:{c['id']})",
                                       callback_data=f"cu_ch:{mid}:{c['id']}")]
                for c in chs[:PAGE_SIZE]]
        btns.append([
            InlineKeyboardButton("��️ Back",  callback_data=f"cu_back:{mid}"),
            InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}"),
        ])
        await cb.message.edit(
            f"📼 <b>{html.escape(genre)}</b> — {len(chs)} catchup channels:",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML)
        return await cb.answer()

    if data.startswith("cu_back:"):
        mid    = int(data.split(":")[1])
        d      = _sess.get(mid, {})
        genres = d.get("genres", {})
        btns   = [[InlineKeyboardButton(f"📼 {g} ({len(cs)})",
                                         callback_data=f"cu_genre:{mid}:{g[:28]}")]
                  for g, cs in list(genres.items())[:20]]
        btns.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}")])
        await cb.message.edit(
            "📼 <b>Catchup TV</b>\n\nSelect a genre:",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML)
        return await cb.answer()

    if data.startswith("cu_ch:"):
        _, mid_s, cid_arg = data.split(":")
        mid = int(mid_s)
        d   = _sess.get(mid, {})
        # find channel name stored in session
        cname_found = cid_arg
        for g, cs in d.get("genres",{}).items():
            for c in cs:
                if c["id"] == cid_arg:
                    cname_found = c["name"]; break
        btns = []
        for off in range(0, -8, -1):
            dt  = ist_now() + timedelta(days=off)
            lbl = ("Today" if off==0 else "Yesterday" if off==-1
                   else dt.strftime("%d %b"))
            btns.append([InlineKeyboardButton(
                f"📅 {lbl}",
                callback_data=f"cu_date:{cid_arg}:{off}")])
        btns.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{mid}")])
        await cb.message.edit(
            f"📼 <b>{html.escape(cname_found)}</b>\n\nSelect a date:",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML)
        return await cb.answer()

    if data.startswith("cu_date:"):
        _, cid_arg, off_s = data.split(":")
        offset = int(off_s)
        await cb.answer("Fetching programs…")
        chs  = await asyncio.to_thread(fetch_channels)
        ch   = next((c for c in chs if _ch_id(c) == cid_arg), None)
        if not ch:
            return await cb.message.reply("❌ Channel not found.",
                                           parse_mode=enums.ParseMode.HTML)
        epg = await asyncio.to_thread(fetch_epg, cid_arg, offset)
        if not epg:
            return await cb.message.reply("❌ No catchup data found.",
                                           parse_mode=enums.ParseMode.HTML)
        progs = (epg.get("epg") or epg.get("programs") or
                 epg.get("result") or [])
        if not progs:
            return await cb.message.reply("ℹ️ No programs for this date.",
                                           parse_mode=enums.ParseMode.HTML)
        date_s = epg.get("serverDate","")[:10] or ""
        smsg   = await cb.message.reply("📋 <b>Loading programs…</b>",
                                         parse_mode=enums.ParseMode.HTML)
        mid    = smsg.id
        _sess[mid] = {
            "type":     "crip_programs",
            "programs": progs,
            "ch":       ch,
            "date_s":   date_s,
            "uid":      uid,
            "page":     0,
        }
        await smsg.edit(
            f"📼 <b>{html.escape(_ch_name(ch))}</b>\n"
            f"📅 {date_s}  —  {len(progs)} programs\n\n"
            f"Tap a program to download:",
            reply_markup=_programs_kb(mid, progs, 0),
            parse_mode=enums.ParseMode.HTML)
        return

    # ───────────────────────────────────────────────��─────
    # PROGRAM LIST PAGINATION
    # ─────────────────────────────────────────────────────
    if data.startswith("ppage:"):
        _, mid_s, pg_s = data.split(":")
        mid = int(mid_s); page = int(pg_s)
        d   = _sess.get(mid)
        if not d:
            return await cb.answer("Session expired.", show_alert=True)
        d["page"] = page
        await cb.message.edit_reply_markup(
            _programs_kb(mid, d["programs"], page))
        return await cb.answer()

    # ─────────────────────────────────────────────────────
    # PROGRAM SELECTED → START CATCHUP DOWNLOAD
    # ─────────────────────────────────────────────────────
    if data.startswith("ppick:"):
        _, mid_s, pi_s = data.split(":")
        mid = int(mid_s); pi = int(pi_s)
        d   = _sess.get(mid)
        if not d:
            return await cb.answer("Session expired. Run /crip again.",
                                    show_alert=True)
        if d.get("uid") != uid:
            return await cb.answer("Not your session.", show_alert=True)
        if uid in _active_rec:
            return await cb.answer("Already recording! /cancel first.",
                                    show_alert=True)
        prog    = d["programs"][pi]
        ch      = d["ch"]
        cid_arg = _ch_id(ch)
        srno    = str(prog.get("srno") or prog.get("id") or "")
        begin   = str(prog.get("startEpoch") or prog.get("begin") or "")
        end_v   = str(prog.get("endEpoch")   or prog.get("end")   or "")

        try:
            b_sec   = epoch_to_sec(begin)
            e_sec   = epoch_to_sec(end_v)
            dur_sec = max(int(e_sec - b_sec), 60)
        except Exception:
            dur_sec = 1800
        dur_str = hms(dur_sec)

        await cb.answer("⏳ Starting download…")
        smsg = await cb.message.reply("⏳ <b>Getting catchup stream URL…</b>",
                                       parse_mode=enums.ParseMode.HTML)
        url = await asyncio.to_thread(
            get_stream_url, cid_arg, "Catchup", srno, begin, end_v)
        if not url:
            await smsg.edit("❌ <b>Could not get catchup stream URL.</b>\n\n"
                             "This program may no longer be available.",
                             parse_mode=enums.ParseMode.HTML)
            return
        probe        = await asyncio.to_thread(ffprobe, url)
        v_opts, a_opts = parse_probe(probe)
        t = asyncio.create_task(do_record(
            client, cb.message.chat.id, ch, dur_str, f"{cid_arg}_{srno}",
            smsg, url,
            v_opts[0]["index"] if v_opts else None,
            [a["index"] for a in a_opts],
            v_opts[0]["label"] if v_opts else "best",
            a_opts))
        _active_rec[uid] = t
        _sess.pop(mid, None)
        return

    # ─────────────────────────────────────────────────────
    # RECORD QUALITY / AUDIO PICKER CALLBACKS
    # ─────────────────────────────────────────────────────
    if data.startswith("qsel:"):
        _, mid_s, idx_s = data.split(":")
        mid = int(mid_s); idx = int(idx_s)
        d   = _sess.get(mid)
        if not d or d.get("uid") != uid:
            return await cb.answer("Session expired.", show_alert=True)
        vo = next((v for v in d["v_opts"] if v["index"]==idx), None)
        if vo:
            d["sel_vid"] = idx
            d["quality"] = vo["label"]
        await cb.message.edit_reply_markup(_picker_kb(mid))
        return await cb.answer()

    if data.startswith("asel:"):
        _, mid_s, idx_s = data.split(":")
        mid = int(mid_s); idx = int(idx_s)
        d   = _sess.get(mid)
        if not d or d.get("uid") != uid:
            return await cb.answer("Session expired.", show_alert=True)
        sel = set(d.get("sel_aud", []))
        if idx in sel: sel.discard(idx)
        else:          sel.add(idx)
        if not sel: sel.add(idx)  # always keep at least one
        d["sel_aud"] = sorted(sel)
        d["all_audio"] = False
        await cb.message.edit_reply_markup(_picker_kb(mid))
        return await cb.answer()

    if data.startswith("aall:"):
        mid = int(data.split(":")[1])
        d   = _sess.get(mid)
        if not d or d.get("uid") != uid:
            return await cb.answer("Session expired.", show_alert=True)
        d["all_audio"] = not d.get("all_audio", True)
        if d["all_audio"]:
            d["sel_aud"] = [a["index"] for a in d.get("a_opts", [])]
        await cb.message.edit_reply_markup(_picker_kb(mid))
        return await cb.answer()

    if data.startswith("rstart:"):
        mid = int(data.split(":")[1])
        d   = _sess.get(mid)
        if not d or d.get("uid") != uid:
            return await cb.answer("Session expired.", show_alert=True)
        if uid in _active_rec:
            return await cb.answer("Already recording! /cancel first.",
                                    show_alert=True)
        await cb.answer("▶️ Starting…")
        await cb.message.edit("⏳ <b>Starting recording…</b>",
                               parse_mode=enums.ParseMode.HTML)
        t = asyncio.create_task(do_record(
            client, cb.message.chat.id,
            d["ch"], d["dur"], _ch_id(d["ch"]),
            cb.message, d["url"],
            d.get("sel_vid"), d.get("sel_aud"),
            d.get("quality", "best"), d.get("a_opts")))
        _active_rec[uid] = t
        _sess.pop(mid, None)
        return

    if data.startswith("rcancel:"):
        mid = int(data.split(":")[1])
        _sess.pop(mid, None)
        try: await cb.message.edit("❎ <b>Cancelled.</b>",
                                    parse_mode=enums.ParseMode.HTML)
        except Exception: pass
        return await cb.answer()

    await cb.answer()

# ══ Entry point ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR,     exist_ok=True)
    print("╔══════════════════════════════════════════════════╗")
    print(f"║   JioTV PRO Bot  ·  {RELEASE_TAG}          ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"   Account  : {_CREDS['name']}  ({_CREDS['mobile']})")
    print(f"   SubID    : {_CREDS['subscriberId']}")
    print(f"   DeviceID : {_CREDS['deviceId']}")
    print(f"   Admin    : {ADMIN_ID}")
    print(f"   MongoDB  : {'✅ connected' if _db is not None else '❌ disabled'}")
    print(f"   Downloads: {os.path.abspath(DOWNLOAD_DIR)}")
    print()
    bot.run()
