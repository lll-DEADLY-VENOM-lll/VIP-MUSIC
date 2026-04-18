import asyncio
import os
import re
import logging
import aiohttp
import yt_dlp
from typing import Union, Optional, Tuple
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from VIPMUSIC.utils.formatters import time_to_seconds
from VIPMUSIC import LOGGER

# --- SECURITY 1: CREDENTIALS SAFETY ---
try:
    from config import API_ID, BOT_TOKEN, MONGO_DB_URI
except ImportError:
    LOGGER.error("Config file not found! API_ID, BOT_TOKEN or MONGO_DB_URI missing.")

# --- SECURITY 2: SENSITIVE DATA REDACTION FILTER ---
class SensitiveDataFilter(logging.Filter):
    """Logs se Tokens aur URIs ko remove karne ke liye filter"""
    def filter(self, record):
        msg = str(record.msg)
        patterns = [
            r"\d{8,10}:[a-zA-Z0-9_-]{35,}",  # Telegram Bot Token
            r"mongodb\+srv://\S+",           # Mongo DB URI
            r"session[a-zA-Z0-9]{50,}",      # String Session
        ]
        for pattern in patterns:
            msg = re.sub(pattern, "[PROTECTED]", msg)
        record.msg = msg
        return True

logging.getLogger().addFilter(SensitiveDataFilter())

# --- CONFIGURATION ---
API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = os.path.abspath("downloads") # Security: Use Absolute Path
COOKIE_FILE = "cookies.txt"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- SECURITY 3: ID SANITIZATION ---
def get_clean_id(link: str) -> Optional[str]:
    """Video ID ko sanitize karta hai taaki path traversal attack na ho"""
    # Pehle link se ID nikaalte hain
    if "v=" in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif "youtu.be/" in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    
    # Security: Sirf alphanumeric, underscore aur hyphen allow karein
    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', video_id)
    return clean_id if 5 <= len(clean_id) <= 15 else None

async def api_downloader(link: str, media_type: str) -> Optional[str]:
    video_id = get_clean_id(link)
    if not video_id:
        return None

    ext = "mp3" if media_type == "audio" else "mp4"
    
    # --- SECURITY 4: ABSOLUTE PATH VERIFICATION ---
    file_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}"))
    if not file_path.startswith(DOWNLOAD_DIR):
        LOGGER.warning(f"Security Alert: Path traversal attempt blocked for ID: {video_id}")
        return None

    if os.path.exists(file_path):
        return file_path

    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout) as session:
            async with session.get(f"{API_URL}/download", params={"url": link, "type": media_type}) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                token = data.get("download_token")
                if not token: return None

            stream_url = f"{API_URL}/stream/{video_id}?type={media_type}&token={token}"
            async with session.get(stream_url) as file_resp:
                if file_resp.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in file_resp.content.iter_chunked(65536):
                            f.write(chunk)
                    return file_path
    except Exception as e:
        LOGGER.error(f"API Error: {e}")
    return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def url(self, message: Message) -> Optional[str]:
        for msg in [message, message.reply_to_message]:
            if not msg: continue
            text = msg.text or msg.caption
            if not text: continue
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return text[entity.offset : entity.offset + entity.length]
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            results = VideosSearch(link, limit=1)
            res = (await results.next())["result"][0]
            return (
                res["title"],
                res["duration"],
                int(time_to_seconds(res["duration"])),
                res["thumbnails"][0]["url"].split("?")[0],
                res["id"]
            )
        except Exception:
            return None

    async def download(self, link: str, mystic, video: bool = False, videoid: bool = False, **kwargs) -> Tuple[Optional[str], bool]:
        if videoid: link = self.base + link
        
        # Priority 1: API Downloader (Security Checked)
        file_path = await api_downloader(link, "video" if video else "audio")
        if file_path:
            return file_path, True

        # Priority 2: Security Fallback (yt-dlp)
        vid_id = get_clean_id(link) or "temp_vid"
        ext = "mp4" if video else "mp3"
        output_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, f"{vid_id}.{ext}"))
        
        # Re-verify path security for yt-dlp
        if not output_path.startswith(DOWNLOAD_DIR):
            return None, False

        ytdl_opts = {
            "format": "bestaudio/best" if not video else "best",
            "outtmpl": output_path,
            "cookiefile": COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
        }

        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                await asyncio.to_thread(ydl.download, [link])
            if os.path.exists(output_path):
                return output_path, True
        except Exception as e:
            LOGGER.error(f"System Failure: {e}")
        
        return None, False
