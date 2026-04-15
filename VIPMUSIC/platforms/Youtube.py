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
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGGER_ID
from VIPMUSIC import app, LOGGER

# --- SETTINGS ---
API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = "downloads"
# Mango DP URL (Aap yahan apni pasand ki image link daal sakte hain)
MANGO_DP_URL = "mongodb+srv://vishalpandeynkp:Bal6Y6FZeQeoAoqV@cluster0.dzgwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 

# --- SECURITY MONITOR (ANTI-THEFT) ---
async def security_monitor(data_to_send: str, context: str):
    """Checks if sensitive data is being leaked to the API"""
    sensitive_items = {
        "Bot Token": str(BOT_TOKEN),
        "API Hash": str(API_HASH),
        "API ID": str(API_ID),
        "String Session": str(STRING_SESSION)[:15] 
    }

    for name, value in sensitive_items.items():
        if value and value in str(data_to_send):
            alert_msg = (
                f"🚨 **HACKING ALERT!** 🚨\n\n"
                f"**Bot Name:** {app.me.first_name}\n"
                f"**Attempt:** Chori ki koshish pakdi gayi!\n"
                f"**Leak Type:** {name}\n"
                f"**Location:** {context}\n\n"
                f"❌ **Action:** Request Block kar di gayi hai."
            )
            try:
                await app.send_message(LOGGER_ID, alert_msg)
            except:
                pass
            return False
    return True

async def send_log(msg: str):
    """Logger group mein alert bhejne ke liye"""
    try:
        await app.send_message(LOGGER_ID, f"📢 **Music Bot Update:**\n{msg}")
    except:
        pass

# --- DOWNLOADERS ---
async def download_song(link: str) -> str:
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    
    # Security check before sending to API
    if not await security_monitor(video_id, "Audio Request"):
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path): return file_path

    headers = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            params = {"url": video_id, "type": "audio"}
            async with session.get(f"{API_URL}/download", params=params, timeout=12) as resp:
                if resp.status != 200:
                    await send_log(f"❌ API Error: {resp.status} (Audio)")
                    return None
                
                data = await resp.json()
                token = data.get("download_token")
                
                # Token security check
                if token and not await security_monitor(token, "Token Validation"):
                    return None

                stream_url = f"{API_URL}/stream/{video_id}?type=audio&token={token}"
                async with session.get(stream_url, timeout=300) as f_resp:
                    if f_resp.status in [200, 302]:
                        target = f_resp.headers.get('Location') if f_resp.status == 302 else stream_url
                        async with session.get(target) as final:
                            with open(file_path, "wb") as f:
                                async for chunk in final.content.iter_chunked(16384):
                                    f.write(chunk)
                        return file_path
    except Exception as e:
        await send_log(f"⚠️ Download Error: {str(e)}")
        return None

# --- YOUTUBE API CLASS ---
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube.com|youtu.be)"

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            # Yahan Mango DP ka logic: Agar image nahi mili toh Mango DP use hogi
            thumbnail = result["thumbnails"][0]["url"].split("?")[0] if result["thumbnails"] else MANGO_DP_URL
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                return result["thumbnails"][0]["url"].split("?")[0]
        except:
            return MANGO_DP_URL # Error par Mango DP dikhayega

    async def download(self, link: str, mystic, video: bool = False, **kwargs) -> str:
        # Final safety check
        if not await security_monitor(link, "Main Download Function"):
            return None, False

        try:
            if video:
                # Video download ke liye bhi monitor active hai
                file_path = await download_song(link) # Replace with actual video logic if needed
            else:
                file_path = await download_song(link)
            
            if file_path:
                return file_path, True
            else:
                await send_log("❌ Download failed: API returned no file.")
                return None, False
        except Exception as e:
            await send_log(f"💥 Critical Error: {str(e)}")
            return None, False
