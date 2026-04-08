import os
import re
import time
import json
import math
import html
import asyncio
import subprocess
from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- CONFIGURATION ---
API_ID = 20093900
API_HASH = "314286d8af54eda517ff6f3974fd3aad"
BOT_TOKEN = "8447401622:AAEpNjFqr2wP5bzTvgv1VCPx8x9PfPV_rFY"
OWNER_ID = 5009476236
M3U_URL = "https://jioplaylist.joinus-apiworker.workers.dev/playlist.m3u"

PAGE_SIZE = 10
REQUEST_TIMEOUT = (15, 60)
THUMB_TIMESTAMP = "00:00:02"
THUMB_WIDTH = 320
MAX_AUDIO_BUTTONS = 12
PROGRESS_UPDATE_SEC = 4
PROGRESS_BAR_STYLE = "dark"  # dark / cold / hot
RELEASE_SOURCE = "Jiotv+"
RELEASE_TAG = "DoraemonBro"
if ZoneInfo is not None:
    try:
        TIMEZONE = ZoneInfo("Asia/Kolkata")
    except Exception:
        TIMEZONE = timezone(timedelta(hours=5, minutes=30))
else:
    TIMEZONE = timezone(timedelta(hours=5, minutes=30))


app = Client("jiotv_plus_pro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

temp_db: Dict[int, Dict] = {}


def build_http_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def parse_extinf_name(line: str) -> str:
    if "," in line:
        tail = line.split(",", 1)[1].strip()
        if tail:
            return tail
    m = re.search(r'tvg-name="([^"]+)"', line, re.I)
    if m:
        return m.group(1).strip()
    return "Unknown"


def extract_license_key(line: str) -> str:
    m = re.search(r'license_key=([^\s]+)', line, re.I)
    if not m:
        return ""
    raw = m.group(1).strip().strip('"')
    if ":" in raw:
        parts = raw.split(":")
        if parts[-1].strip():
            return parts[-1].strip()
    return raw


def finalize_entry(channels: List[Dict], current: Optional[Dict], seen: set) -> None:
    if not current:
        return
    url = (current.get("url") or "").strip()
    name = (current.get("name") or "Unknown").strip()
    if not url:
        return
    key = (name.lower(), url)
    if key in seen:
        return
    seen.add(key)
    channels.append({
        "name": name,
        "url": url,
        "key": (current.get("key") or "").strip(),
        "ua": (current.get("ua") or "").strip(),
        "cookie": (current.get("cookie") or "").strip(),
    })


def fetch_all_channels() -> List[Dict]:
    channels: List[Dict] = []
    current: Optional[Dict] = None
    seen = set()

    try:
        session = build_http_session()
        resp = session.get(M3U_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        response_text = resp.text

        for raw_line in response_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("#EXTINF"):
                finalize_entry(channels, current, seen)
                current = {"name": parse_extinf_name(line)}
                continue

            if current is None:
                continue

            if "license_key=" in line:
                current["key"] = extract_license_key(line)
                continue

            if "user-agent=" in line.lower():
                ua_match = re.search(r'user-agent=([^\s]+.*)$', line, re.I)
                if ua_match:
                    current["ua"] = ua_match.group(1).strip().strip('"')
                continue

            if line.startswith("#EXTHTTP:"):
                try:
                    payload = json.loads(line.replace("#EXTHTTP:", "", 1).strip())
                    cookie = payload.get("cookie") or payload.get("Cookie") or ""
                    if cookie:
                        current["cookie"] = cookie
                    headers = payload.get("headers") or {}
                    if not current.get("ua"):
                        current["ua"] = headers.get("User-Agent", "")
                except Exception:
                    pass
                continue

            if line.startswith("#EXTVLCOPT:http-user-agent="):
                current["ua"] = line.split("=", 1)[1].strip()
                continue

            if line.startswith(("http://", "https://")):
                current["url"] = line
                finalize_entry(channels, current, seen)
                current = None
                continue

        finalize_entry(channels, current, seen)

    except Exception as e:
        print(f"Fetch Error: {e}")

    return channels


def build_headers(ua: str, cookie: str) -> str:
    header_lines = []
    if ua:
        header_lines.append(f"User-Agent: {ua}")
    if cookie:
        header_lines.append(f"Cookie: {cookie}")
    return "\r\n".join(header_lines) + ("\r\n" if header_lines else "")


def ffprobe_streams(url: str, ua: str = "", cookie: str = "", key: str = "") -> Dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
    ]
    headers = build_headers(ua, cookie)
    if headers:
        cmd.extend(["-headers", headers])
    if key:
        cmd.extend(["-cenc_decryption_key", key])
    cmd.append(url)
    raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return json.loads(raw.decode("utf-8", errors="ignore"))


def normalize_lang(value: str) -> str:
    value = (value or '').strip().lower()
    mapping = {
        'hin': 'Hindi', 'eng': 'English', 'en': 'English', 'tam': 'Tamil', 'tel': 'Telugu',
        'kan': 'Kannada', 'mal': 'Malayalam', 'ben': 'Bengali', 'guj': 'Gujarati',
        'mar': 'Marathi', 'und': 'Unknown', '': 'Unknown',
    }
    return mapping.get(value, value.title())


def short_lang(value: str) -> str:
    value = normalize_lang(value)
    mapping = {
        "Hindi": "Hin", "English": "Eng", "Tamil": "Tam", "Telugu": "Tel",
        "Kannada": "Kan", "Malayalam": "Mal", "Bengali": "Ben",
        "Gujarati": "Guj", "Marathi": "Mar", "Unknown": "Und",
    }
    return mapping.get(value, re.sub(r"[^A-Za-z0-9]", "", value)[:3].title() or "Und")


def sanitize_release_title(name: str) -> str:
    name = (name or "Unknown").strip()
    cleaned = re.sub(r'[\/:*?"<>|]+', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "Unknown"


def codec_label(codec_name: str) -> str:
    codec = (codec_name or "").lower()
    mapping = {"h264": "H264", "hevc": "H265", "h265": "H265", "aac": "AAC", "ac3": "AC3", "eac3": "EAC3"}
    return mapping.get(codec, codec.upper() or "UNK")


def audio_channel_label(channels: int) -> str:
    if channels <= 0:
        return "2.0"
    if channels == 1:
        return "1.0"
    if channels == 2:
        return "2.0"
    return f"{channels}.0"


def parse_duration_to_seconds(value: str) -> int:
    try:
        parts = [int(x) for x in value.strip().split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 1:
            return parts[0]
    except Exception:
        pass
    return 0


def seconds_to_hms(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def parse_ffmpeg_time_to_seconds(value: str) -> float:
    try:
        h, m, s = value.strip().split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        return 0.0


def get_stream_bitrate(s: Dict) -> int:
    tags = s.get('tags') or {}
    candidates = [
        s.get('bit_rate'),
        tags.get('variant_bitrate'), tags.get('VARIANT_BITRATE'),
        tags.get('BPS'), tags.get('bps'),
    ]
    for item in candidates:
        try:
            value = int(float(item))
            if value > 0:
                return value
        except Exception:
            continue
    return 0


def build_progress_bar(percent: float, style: str = PROGRESS_BAR_STYLE, width: int = 10) -> str:
    pct = max(0.0, min(100.0, percent))
    filled = int(round((pct / 100.0) * width))
    if style == "cold":
        return f"❲ {'■' * filled}{'▢' * (width - filled)} ❳"
    if style == "hot":
        width = 16
        filled = int(round((pct / 100.0) * width))
        return f"[{'█' * filled}{'░' * (width - filled)}]"
    return f"[{'⬢' * filled}{'⬡' * (width - filled)}]"


def build_release_caption(base_title: str, start_dt: datetime, duration_sec: int, quality_text: str, audio_labels: List[str], audio_codec: str, audio_channels: int, video_codec: str, ext: str = 'mp4') -> str:
    end_dt = start_dt + timedelta(seconds=max(1, duration_sec))
    audio_part = '-'.join(short_lang(a) for a in audio_labels) or 'Und'
    release_title = sanitize_release_title(base_title)
    return (
        f"{release_title}[{start_dt.strftime('%I:%M%p')}-{end_dt.strftime('%I:%M%p')}]"
        f"[{start_dt.strftime('%d-%m-%Y')}].{quality_text}.{RELEASE_SOURCE}.WEB-DL."
        f"[{audio_part}].{audio_codec}.{audio_channel_label(audio_channels)}.{video_codec}-{RELEASE_TAG}.{ext}"
    )


def build_picker_text(ch_name: str, quality_label: Optional[str], audio_indexes: List[int]) -> str:
    return (
        "🎛️ <b>Quality & Audio Panel</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📺 <b>Channel:</b> <code>{html.escape(ch_name)}</code>\n"
        f"🎞 <b>Selected:</b> <code>{html.escape(quality_label or 'best')}</code>\n"
        f"🔊 <b>Audio Tracks:</b> <code>{len(audio_indexes)}</code>"
    )


def build_status_text(action: str, percent: float, speed_kb: float, eta: str, extra_label: str = "Speed") -> str:
    return (
        f"📤 <b>{action}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{build_progress_bar(percent)} <b>{percent:.1f}%</b>\n"
        f"⚡ <b>{extra_label}:</b> <code>{speed_kb:.2f} KB/s</code>\n"
        f"⏳ <b>ETA:</b> <code>{eta}</code>"
    )


def stream_quality_label(s: Dict) -> str:
    h = int(s.get('height') or 0)
    w = int(s.get('width') or 0)
    br = get_stream_bitrate(s)
    br_text = f"{round(br/1000)}k" if br else "?k"
    if h:
        return f"{h}p - {br_text}"
    if w:
        return f"{w}w - {br_text}"
    if br:
        return br_text
    return f"v{int(s.get('index') or 0)}"


def quality_release_label(label: Optional[str]) -> str:
    raw = (label or 'best').strip()
    m = re.search(r'(\d{3,4}p)', raw, re.I)
    if m:
        return m.group(1)
    return raw.replace(' ', '')


def build_stream_options(probe: Dict) -> Tuple[List[Dict], List[Dict]]:
    streams = probe.get('streams') or []
    videos = [s for s in streams if s.get('codec_type') == 'video']
    audios = [s for s in streams if s.get('codec_type') == 'audio']

    def video_score(s: Dict):
        return (int(s.get('height') or 0), int(s.get('width') or 0), int(s.get('bit_rate') or 0), -int(s.get('index') or 0))

    videos_sorted = sorted(videos, key=video_score, reverse=True)
    video_options = []
    seen_q = set()
    for s in videos_sorted:
        label = stream_quality_label(s)
        key = (label, int(s.get('index') or 0))
        if key in seen_q:
            continue
        seen_q.add(key)
        video_options.append({
            'index': int(s.get('index') or 0),
            'label': label,
            'height': int(s.get('height') or 0),
            'width': int(s.get('width') or 0),
            'bit_rate': int(s.get('bit_rate') or 0),
        })

    audio_options = []
    for s in audios:
        idx = int(s.get('index') or 0)
        tags = s.get('tags') or {}
        lang = normalize_lang(tags.get('language') or tags.get('LANGUAGE') or '')
        title = (tags.get('title') or tags.get('NAME') or '').strip()
        br = int(s.get('bit_rate') or 0)
        suffix = f" - {round(br/1000)}k" if br else ''
        text = f"{lang}{suffix}"
        if title and title.lower() not in text.lower():
            text = f"{lang} ({title}){suffix}"
        audio_options.append({
            'index': idx,
            'label': text,
            'lang': lang,
            'bit_rate': br,
        })

    if len(audio_options) > 1:
        audio_options = sorted(audio_options, key=lambda a: (a['lang'], -a['bit_rate'], a['index']))
    return video_options, audio_options


def default_best_selection(video_options: List[Dict], audio_options: List[Dict]) -> Tuple[Optional[int], List[int], Optional[str]]:
    best_video_idx = video_options[0]['index'] if video_options else None
    quality_label = video_options[0]['label'] if video_options else None
    audio_indexes = [a['index'] for a in audio_options]
    return best_video_idx, audio_indexes, quality_label


def run_subprocess(cmd: List[str]) -> Tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stderr or proc.stdout or ""


def remux_ts_to_mp4(ts: str, mp4: str) -> None:
    cmd = ["ffmpeg", "-y", "-i", ts, "-map", "0", "-c", "copy", mp4]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def extract_thumbnail(video_path: str, thumb_path: str) -> bool:
    commands = [
        [
            "ffmpeg", "-y",
            "-ss", THUMB_TIMESTAMP,
            "-i", video_path,
            "-frames:v", "1",
            "-vf", f"thumbnail,scale='min({THUMB_WIDTH},iw)':-2",
            "-pix_fmt", "yuvj420p",
            "-q:v", "4",
            "-strict", "unofficial",
            thumb_path,
        ],
        [
            "ffmpeg", "-y",
            "-ss", THUMB_TIMESTAMP,
            "-i", video_path,
            "-frames:v", "1",
            "-vf", f"thumbnail,scale='min({THUMB_WIDTH},iw)':-2",
            "-q:v", "4",
            thumb_path,
        ],
    ]
    for cmd in commands:
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        rc, _ = run_subprocess(cmd)
        if rc == 0 and os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
            return True
    return False


async def consume_ffmpeg_progress(stream, total_sec: int, temp_path: str, status_msg, start_time: float, state: Dict):
    latest_sec = 0.0
    while True:
        line = await stream.readline()
        if not line:
            break
        text = line.decode(errors="ignore").strip()
        if not text or "=" not in text:
            continue
        key, value = text.split("=", 1)
        if key == "out_time":
            latest_sec = parse_ffmpeg_time_to_seconds(value)
        elif key in ("out_time_us", "out_time_ms"):
            try:
                latest_sec = float(value) / 1_000_000.0
            except Exception:
                pass
        elif key == "progress" and value == "end":
            latest_sec = float(total_sec or latest_sec)

        if total_sec > 0 and latest_sec >= 0:
            now = time.time()
            last = state.get("last", 0.0)
            if (now - last) >= PROGRESS_UPDATE_SEC:
                state["last"] = now
                percent = min(100.0, (latest_sec / total_sec) * 100.0)
                size_bytes = os.path.getsize(temp_path) if os.path.exists(temp_path) else 0
                speed_kb = (size_bytes / max(now - start_time, 1e-6)) / 1024.0
                eta = seconds_to_hms(max(total_sec - latest_sec, 0))
                try:
                    await status_msg.edit(
                        build_status_text("Downloading stream...", percent, speed_kb, eta, extra_label="Write"),
                        parse_mode=enums.ParseMode.HTML,
                    )
                except Exception:
                    pass

async def record_and_upload(client, chat_id, ch, duration, filename, status_msg, selected_video_idx=None, selected_audio_indexes=None, selected_quality_label=None):
    ts = f"{filename}.ts"
    mp4 = f"{filename}.mp4"
    jpg = f"{filename}.jpg"

    capture_start = datetime.now(TIMEZONE)
    requested_duration_sec = max(1, parse_duration_to_seconds(duration))
    await status_msg.edit(
        build_status_text("Downloading stream...", 0, 0, seconds_to_hms(requested_duration_sec), extra_label="Write"),
        parse_mode=enums.ParseMode.HTML,
    )

    headers = build_headers(ch.get("ua", ""), ch.get("cookie", ""))

    best_video_idx = selected_video_idx
    audio_indexes: List[int] = list(selected_audio_indexes or [])
    quality_label = selected_quality_label
    probe_error = None
    video_options: List[Dict] = []
    audio_options: List[Dict] = []
    try:
        probe = ffprobe_streams(ch["url"], ch.get("ua", ""), ch.get("cookie", ""), ch.get("key", ""))
        video_options, audio_options = build_stream_options(probe)
        auto_video_idx, auto_audio_indexes, auto_quality_label = default_best_selection(video_options, audio_options)
        if best_video_idx is None:
            best_video_idx = auto_video_idx
        if not audio_indexes:
            audio_indexes = auto_audio_indexes
        if not quality_label:
            quality_label = auto_quality_label
    except Exception as e:
        probe_error = str(e)

    cmd = ["ffmpeg", "-y", "-progress", "pipe:1", "-nostats"]
    if headers:
        cmd.extend(["-headers", headers])
    if ch.get("key"):
        cmd.extend(["-cenc_decryption_key", ch["key"]])
    cmd.extend(["-i", ch["url"], "-t", duration])

    if best_video_idx is not None:
        cmd.extend(["-map", f"0:{best_video_idx}"])
    if audio_indexes:
        for idx in audio_indexes:
            cmd.extend(["-map", f"0:{idx}"])
    if best_video_idx is None and not audio_indexes:
        cmd.extend(["-map", "0"])

    cmd.extend(["-c", "copy", "-ignore_unknown", ts])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    progress_state = {"last": 0.0}
    progress_task = asyncio.create_task(
        consume_ffmpeg_progress(process.stdout, requested_duration_sec, ts, status_msg, time.time(), progress_state)
    )
    await process.wait()
    stderr_bytes = await process.stderr.read()
    await progress_task
    stderr_text = stderr_bytes.decode(errors="ignore")

    if not os.path.exists(ts) or os.path.getsize(ts) < 1000:
        extra = f"\nProbe: {probe_error}" if probe_error else ""
        return await status_msg.edit(
            f"❌ <b>Recording failed.</b>\n\n<code>{html.escape(stderr_text[-350:])}</code>{html.escape(extra)}",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        await status_msg.edit(
            build_status_text("Download complete. Finalizing...", 100, 0, "00:00:00", extra_label="Write"),
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception:
        pass

    remux_ts_to_mp4(ts, mp4)
    thumb_ok = extract_thumbnail(mp4, jpg)

    meta_cmd = [
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", mp4,
    ]
    try:
        meta = json.loads(subprocess.check_output(meta_cmd).decode().strip() or "{}")
    except Exception:
        meta = {}

    try:
        v_dur = int(float((meta.get('format') or {}).get('duration') or 0))
    except Exception:
        v_dur = 0

    streams = meta.get('streams') or []
    video_stream = next((s for s in streams if s.get('codec_type') == 'video'), {})
    audio_streams = [s for s in streams if s.get('codec_type') == 'audio']

    if not quality_label:
        quality_label = stream_quality_label(video_stream) if video_stream else 'best'
    video_codec = codec_label(video_stream.get('codec_name') or 'h264')
    audio_codec = codec_label(audio_streams[0].get('codec_name') if audio_streams else 'aac')
    audio_channels = int(audio_streams[0].get('channels') or 2) if audio_streams else 2

    selected_audio_map = {a.get('index'): a.get('lang') or a.get('label') or 'Unknown' for a in audio_options}
    audio_labels = [selected_audio_map.get(idx, 'Unknown') for idx in audio_indexes] or ['Unknown']

    release_name = build_release_caption(
        base_title=filename,
        start_dt=capture_start,
        duration_sec=v_dur,
        quality_text=quality_release_label(quality_label),
        audio_labels=audio_labels,
        audio_codec=audio_codec,
        audio_channels=audio_channels,
        video_codec=video_codec,
        ext='mp4',
    )

    await status_msg.edit(build_status_text("Uploading to Telegram...", 0, 0, "00:00:00"), parse_mode=enums.ParseMode.HTML)
    start_time = time.time()
    upload_state = {"last": 0.0}

    try:
        await client.send_video(
            chat_id=chat_id,
            video=mp4,
            thumb=jpg if thumb_ok else None,
            duration=v_dur,
            supports_streaming=True,
            caption=f"<code>{html.escape(release_name)}</code>",
            parse_mode=enums.ParseMode.HTML,
            progress=progress_bar,
            progress_args=(status_msg, start_time, "Uploading to Telegram...", upload_state),
        )
    except Exception as e:
        await client.send_message(chat_id, f"❌ Upload error: {e}")
    finally:
        for f in [ts, mp4, jpg]:
            if os.path.exists(f):
                os.remove(f)
        try:
            await status_msg.delete()
        except Exception:
            pass


async def progress_bar(current, total, message, start_time, action, state):
    now = time.time()
    diff = now - start_time
    if diff <= 0:
        return
    last = state.get("last", 0.0)
    if current != total and (now - last) < PROGRESS_UPDATE_SEC:
        return
    state["last"] = now
    percent = current * 100 / total if total else 0
    speed = current / diff if diff > 0 else 0
    eta = time.strftime("%H:%M:%S", time.gmtime(round((total - current) / speed))) if speed > 0 and total else "00:00:00"
    try:
        await message.edit(build_status_text(action, percent, speed / 1024, eta), parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass




async def safe_cb_answer(cb: CallbackQuery, text: Optional[str] = None, show_alert: bool = False):
    if getattr(cb, "_answered", False):
        return None
    try:
        cb._answered = True
        return await cb.answer(text or "", show_alert=show_alert)
    except Exception:
        return None

def build_quality_audio_markup(msg_id: int) -> InlineKeyboardMarkup:
    data = temp_db[msg_id]
    video_options = data.get('video_options') or []
    audio_options = data.get('audio_options') or []
    selected_video_idx = data.get('selected_video_idx')
    selected_audio_indexes = set(data.get('selected_audio_indexes') or [])

    buttons = []
    if video_options:
        buttons.append([InlineKeyboardButton('🎞 Quality', callback_data=f'noop:{msg_id}:0')])
        row = []
        for v in video_options[:6]:
            prefix = '✅ ' if selected_video_idx == v['index'] else ''
            row.append(InlineKeyboardButton(f"{prefix}{v['label']}", callback_data=f"qsel:{msg_id}:{v['index']}"))
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

    if audio_options:
        buttons.append([InlineKeyboardButton('🔊 Audio', callback_data=f'noop:{msg_id}:0')])
        buttons.append([InlineKeyboardButton(('✅ ' if data.get('all_audio') else '') + 'All Audio', callback_data=f'aall:{msg_id}:0')])
        for a in audio_options[:MAX_AUDIO_BUTTONS]:
            prefix = '✅ ' if a['index'] in selected_audio_indexes and not data.get('all_audio') else ''
            buttons.append([InlineKeyboardButton(f"{prefix}{a['label']}", callback_data=f"asel:{msg_id}:{a['index']}")])

    buttons.append([
        InlineKeyboardButton('▶️ Start', callback_data=f'startrec:{msg_id}:0'),
        InlineKeyboardButton('❌ Cancel', callback_data=f'close:{msg_id}:0'),
    ])
    return InlineKeyboardMarkup(buttons)


def build_match_markup(msg_id: int, page: int) -> InlineKeyboardMarkup:
    data = temp_db[msg_id]
    matches = data["matches"]
    total = len(matches)
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, total)

    buttons = [
        [InlineKeyboardButton(matches[i]["name"], callback_data=f"select:{msg_id}:{i}")]
        for i in range(start, end)
    ]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page:{msg_id}:{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{msg_id}:{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("❌ Close", callback_data=f"close:{msg_id}:0")])
    return InlineKeyboardMarkup(buttons)


@app.on_message(filters.command("dl") & filters.user(OWNER_ID))
async def dl_cmd(client, message: Message):
    args = message.text.split(" ", 3)
    if len(args) < 4:
        return await message.reply("❌ **Format:** `/dl <name> <hh:mm:ss> <filename>`")

    query, duration, filename = args[1].lower(), args[2], args[3]
    all_channels = fetch_all_channels()
    matches = [c for c in all_channels if query in c["name"].lower()]

    if not matches:
        return await message.reply(f"❌ Channel `{query}` was not found. Please check `/list`.")

    if len(matches) > 1:
        temp_db[message.id] = {"matches": matches, "duration": duration, "filename": filename}
        return await message.reply(
            f"🔍 **Multiple channels found ({len(matches)}). Please select one:**",
            reply_markup=build_match_markup(message.id, 0),
        )

    status = await message.reply("⏳ **Initializing...**")
    ch = matches[0]
    try:
        probe = ffprobe_streams(ch["url"], ch.get("ua", ""), ch.get("cookie", ""), ch.get("key", ""))
        video_options, audio_options = build_stream_options(probe)
    except Exception as e:
        video_options, audio_options = [], []
        await status.edit(f"⚠️ Probe failed, using auto mode.\n`{str(e)[:250]}`")
        return await record_and_upload(client, message.chat.id, ch, duration, filename, status)

    best_video_idx, best_audio_indexes, quality_label = default_best_selection(video_options, audio_options)
    temp_db[message.id] = {
        "matches": [ch],
        "duration": duration,
        "filename": filename,
        "selected_channel": ch,
        "video_options": video_options,
        "audio_options": audio_options,
        "selected_video_idx": best_video_idx,
        "selected_audio_indexes": best_audio_indexes,
        "selected_quality_label": quality_label,
        "all_audio": True,
    }
    return await status.edit(
        build_picker_text(ch['name'], quality_label, best_audio_indexes),
        reply_markup=build_quality_audio_markup(message.id),
        parse_mode=enums.ParseMode.HTML,
    )


@app.on_callback_query(filters.regex(r"^(select|page|close|noop|qsel|asel|aall|startrec):"))
async def cb_handler(client, cb: CallbackQuery):
    action, msg_id_text, value = cb.data.split(":")
    msg_id = int(msg_id_text)
    data = temp_db.get(msg_id)

    if action == "noop":
        return await safe_cb_answer(cb)

    if action == "close":
        temp_db.pop(msg_id, None)
        try:
            await cb.message.edit("❎ Closed.")
        except Exception:
            pass
        return await safe_cb_answer(cb)

    if not data:
        return await safe_cb_answer(cb, "❌ Session expired. Please run the command again.", show_alert=True)

    if action == "page":
        await safe_cb_answer(cb)
        page = int(value)
        try:
            await cb.message.edit(
                f"🔍 **Multiple channels found ({len(data['matches'])}). Please select one:**",
                reply_markup=build_match_markup(msg_id, page),
            )
        except Exception:
            pass
        return

    if action == "select":
        index = int(value)
        if index < 0 or index >= len(data["matches"]):
            return await safe_cb_answer(cb, "❌ Invalid selection.", show_alert=True)
        await safe_cb_answer(cb)
        selected_ch = data["matches"][index]
        duration = data["duration"]
        filename = data["filename"]
        try:
            probe = ffprobe_streams(selected_ch["url"], selected_ch.get("ua", ""), selected_ch.get("cookie", ""), selected_ch.get("key", ""))
            video_options, audio_options = build_stream_options(probe)
        except Exception as e:
            await cb.message.edit(f"⚠️ Probe failed, using auto mode.\n`{str(e)[:250]}`")
            await safe_cb_answer(cb, "Starting automatic mode...")
            try:
                await record_and_upload(client, cb.message.chat.id, selected_ch, duration, filename, cb.message)
            finally:
                temp_db.pop(msg_id, None)
            return

        best_video_idx, best_audio_indexes, quality_label = default_best_selection(video_options, audio_options)
        data.update({
            "selected_channel": selected_ch,
            "video_options": video_options,
            "audio_options": audio_options,
            "selected_video_idx": best_video_idx,
            "selected_audio_indexes": best_audio_indexes,
            "selected_quality_label": quality_label,
            "all_audio": True,
        })
        await cb.message.edit(
            build_picker_text(selected_ch['name'], quality_label, best_audio_indexes),
            reply_markup=build_quality_audio_markup(msg_id),
            parse_mode=enums.ParseMode.HTML,
        )
        return

    if action == "qsel":
        await safe_cb_answer(cb)
        idx = int(value)
        vo = next((v for v in data.get('video_options', []) if v['index'] == idx), None)
        if vo:
            data['selected_video_idx'] = idx
            data['selected_quality_label'] = vo['label']
        await cb.message.edit_reply_markup(build_quality_audio_markup(msg_id))
        return

    if action == "aall":
        await safe_cb_answer(cb)
        data['all_audio'] = not data.get('all_audio', True)
        if data['all_audio']:
            data['selected_audio_indexes'] = [a['index'] for a in data.get('audio_options', [])]
        await cb.message.edit_reply_markup(build_quality_audio_markup(msg_id))
        return

    if action == "asel":
        await safe_cb_answer(cb)
        idx = int(value)
        current = set(data.get('selected_audio_indexes') or [])
        if idx in current:
            current.remove(idx)
        else:
            current.add(idx)
        data['selected_audio_indexes'] = sorted(current)
        data['all_audio'] = False
        if not data['selected_audio_indexes']:
            data['selected_audio_indexes'] = [idx]
        await cb.message.edit_reply_markup(build_quality_audio_markup(msg_id))
        return

    if action == "startrec":
        ch = data.get('selected_channel') or (data.get('matches') or [None])[0]
        if not ch:
            return await safe_cb_answer(cb, "❌ Session expired.", show_alert=True)
        await cb.message.edit(f"✅ Selected: **{ch['name']}**\nPreparing recording...")
        await safe_cb_answer(cb, "Starting...")
        try:
            await record_and_upload(
                client, cb.message.chat.id, ch, data['duration'], data['filename'], cb.message,
                selected_video_idx=data.get('selected_video_idx'),
                selected_audio_indexes=data.get('selected_audio_indexes'),
                selected_quality_label=data.get('selected_quality_label'),
            )
        finally:
            temp_db.pop(msg_id, None)


@app.on_message(filters.command("list") & filters.user(OWNER_ID))
async def list_cmd(c, m):
    chs = fetch_all_channels()
    names = sorted({c["name"] for c in chs}, key=str.lower)
    text = "📺 **Available Channels:**\n\n" + "\n".join([f"• `{name}`" for name in names])
    if len(text) > 4000:
        with open("list.txt", "w", encoding="utf-8") as f:
            f.write(text)
        await m.reply_document("list.txt")
        os.remove("list.txt")
        return
    await m.reply(text)


app.run()
