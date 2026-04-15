import asyncio
import os
import re
import aiohttp
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
from VIPMUSIC.utils.formatters import time_to_seconds

# Config se sensitive data aur IDs uthana
try:
    from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGGER_ID
except ImportError:
    API_ID = API_HASH = BOT_TOKEN = STRING_SESSION = LOGGER_ID = None

from VIPMUSIC import app, LOGGER

# --- SETTINGS ---
API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = "downloads"

# SAHI IMAGE LINK: Yahan sirf photo ka link hona chahiye (.jpg ya .png)
# Maine MongoDB link hata diya hai security ke liye.
MANGO_DP_URL = "mongodb+srv://vishalpandeynkp:Bal6Y6FZeQeoAoqV@cluster0.dzgwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 

# --- SECURITY MONITOR (ANTI-THEFT) ---
async def security_monitor(data_to_send: str, context: str):
    """Checks if sensitive data is being leaked to the API"""
    sensitive_items = {
        "Bot Token": str(BOT_TOKEN),
        "API Hash": str(API_HASH),
        "API ID": str(API_ID),
        "String Session": str(STRING_SESSION)[:15] if STRING_SESSION else None
    }

    for name, value in sensitive_items.items():
        if value and value in str(data_to_send):
            alert_msg = (
                f"🚨 **HACKING ALERT!** 🚨\n\n"
                f"**Bot Name:** {app.me.first_name}\n"
                f"**Attempt:** Data Chori ki koshish block ki gayi!\n"
                f"**Leak Type:** {name}\n"
                f"**Location:** {context}"
            )
            try:
                await app.send_message(LOGGER_ID, alert_msg)
            except:
                pass
            return False
    return True

# --- DOWNLOADERS ---
async def download_song(link: str) -> str:
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    
    if not await security_monitor(video_id, "Audio Request"):
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path): return file_path

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            params = {"url": video_id, "type": "audio"}
            async with session.get(f"{API_URL}/download", params=params, timeout=15) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                token = data.get("download_token")
                
                if token and not await security_monitor(token, "Token Validation"):
                    return None

                stream_url = f"{API_URL}/stream/{video_id}?type=audio&token={token}"
                async with session.get(stream_url, timeout=300) as final:
                    if final.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in final.content.iter_chunked(16384):
                                f.write(chunk)
                        return file_path
    except Exception as e:
        LOGGER(__name__).error(str(e))
        return None

# --- YOUTUBE API CLASS ---
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="

    async def url(self, message: Message):
        """Extracts YouTube URL from message (Fixed AttributeError)"""
        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.URL:
                    return message.text[entity.offset : entity.offset + entity.length]
                elif entity.type == MessageEntityType.TEXT_LINK:
                    return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        results = VideosSearch(link, limit=1)
        res = (await results.next())["result"]
        if not res:
            return None
        
        result = res[0]
        title = result["title"]
        duration_min = result.get("duration")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0] if result["thumbnails"] else MANGO_DP_URL
        vidid = result["id"]
        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            results = VideosSearch(link, limit=1)
            res = (await results.next())["result"]
            return res[0]["thumbnails"][0]["url"].split("?")[0]
        except:
            return MANGO_DP_URL

    async def download(self, link: str, mystic, video: bool = False, **kwargs) -> str:
        if not await security_monitor(link, "Main Download Function"):
            return None, False
        try:
            file_path = await download_song(link)
            if file_path:
                return file_path, True
            return None, False
        except Exception:
            return None, False
