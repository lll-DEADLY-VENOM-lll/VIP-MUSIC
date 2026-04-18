import asyncio
import os
import re
import logging
import aiohttp
import yt_dlp
from typing import Union, Optional, Tuple, List
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch, Playlist
from VIPMUSIC.utils.formatters import time_to_seconds
from VIPMUSIC import LOGGER

# --- CONFIGURATION ---
try:
    from config import API_ID, BOT_TOKEN, MONGO_DB_URI
except ImportError:
    LOGGER.error("Config file not found!")

# --- SECURITY FILTER ---
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        msg = str(record.msg)
        patterns = [r"\d{8,10}:[a-zA-Z0-9_-]{35,}", r"mongodb\+srv://\S+"]
        for pattern in patterns:
            msg = re.sub(pattern, "[PROTECTED]", msg)
        record.msg = msg
        return True

logging.getLogger().addFilter(SensitiveDataFilter())

API_URL = "https://shrutibots.site"

# --- UTILS ---
def get_clean_id(link: str) -> Optional[str]:
    if "v=" in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif "youtu.be/" in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', video_id)
    return clean_id if 5 <= len(clean_id) <= 15 else None

async def get_direct_stream_link(link: str, media_type: str) -> Optional[str]:
    """
    Download karne ke bajaye direct streamable URL return karta hai.
    """
    video_id = get_clean_id(link)
    if not video_id:
        return None

    try:
        timeout = aiohttp.ClientTimeout(total=30) 
        async with aiohttp.ClientSession(headers={"User-Agent": "ShrutiMusicBot/1.0"}, timeout=timeout) as session:
            # Step 1: Token prapt karein
            async with session.get(f"{API_URL}/download", params={"url": video_id, "type": media_type}) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                token = data.get("download_token")
                if not token: return None

            # Step 2: Stream URL generate karein (Download nahi, sirf link)
            stream_url = f"{API_URL}/stream/{video_id}?type={media_type}&token={token}"
            return stream_url
    except Exception as e:
        LOGGER.error(f"Streaming Error: {e}")
    return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        is_url = await self.exists(link)
        try:
            if is_url:
                link = link.split("&")[0]
                results = VideosSearch(link, limit=1)
                res_data = await results.next()
                res = res_data["result"]
            else:
                res = await self.search(link, limit=1)

            if not res: return None
            video = res[0]
            return (
                video["title"],
                video["duration"],
                int(time_to_seconds(video["duration"])),
                video["thumbnails"][0]["url"].split("?")[0],
                video["id"]
            )
        except Exception as e:
            LOGGER.error(f"Details Fetch Error: {e}")
            return None

    async def search(self, query: str, limit: int = 1):
        try:
            search = VideosSearch(query, limit=limit)
            resp = await search.next()
            return resp.get("result", [])
        except Exception:
            return []

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """Direct stream video link"""
        if videoid: link = self.base + link
        stream_link = await get_direct_stream_link(link, "video")
        return (1, stream_link) if stream_link else (0, "Stream Failed")

    async def download(
        self,
        link: str,
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        **kwargs
    ) -> Tuple[Optional[str], bool]:
        """
        Ab ye function file path ke bajaye Direct Stream URL return karega.
        """
        if videoid: link = self.base + link
        m_type = "video" if video else "audio"
        
        # Pehle API se stream link koshish karein
        stream_link = await get_direct_stream_link(link, m_type)
        
        if stream_link:
            return stream_link, True
        
        # Fallback: Agar API fail ho jaye toh yt-dlp se direct link nikalne ki koshish karein
        try:
            ydl_opts = {"format": "bestaudio/best", "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, link, download=False)
                return info['url'], True
        except Exception as e:
            LOGGER.error(f"YTDL Direct Stream Error: {e}")
            return None, False

    async def track(self, query: str, videoid: Union[bool, str] = None):
        det = await self.details(query, videoid)
        if not det: return None, None
        track_details = {
            "title": det[0],
            "link": self.base + det[4],
            "vidid": det[4],
            "duration_min": det[1],
            "thumb": det[3],
        }
        return track_details, det[4]

# Initialize
YouTube = YouTubeAPI()
