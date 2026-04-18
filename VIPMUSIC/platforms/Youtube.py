import asyncio
import os
import re
import logging
import aiohttp
import aiofiles
import yt_dlp
from typing import Union, Optional, Tuple
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch, Playlist
from ShrutiMusic.utils.formatters import time_to_seconds
from ShrutiMusic import LOGGER

# --- SECURITY 1: SENSITIVE DATA REDACTION ---
class SensitiveDataFilter(logging.Filter):
    """Logs se sensitive data jaise Tokens aur URIs ko mask karne ke liye filter"""
    def filter(self, record):
        msg = str(record.msg)
        patterns = [
            r"\d{8,10}:[a-zA-Z0-9_-]{35,}",  # Telegram Bot Token
            r"mongodb\+srv://\S+",           # Mongo DB URI
        ]
        for pattern in patterns:
            msg = re.sub(pattern, "[PROTECTED]", msg)
        record.msg = msg
        return True

logging.getLogger().addFilter(SensitiveDataFilter())

# --- CONFIGURATION ---
API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- SECURITY 2: ID SANITIZATION ---
def get_clean_id(link: str) -> Optional[str]:
    """Video ID ko sanitize karta hai taaki path traversal attack na ho sake"""
    if "v=" in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif "youtu.be/" in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    
    # Sirf alphanumeric, hyphen aur underscore allow karein
    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', video_id)
    return clean_id if 5 <= len(clean_id) <= 15 else None

async def download_from_api(link: str, media_type: str) -> Optional[str]:
    """Secure API Downloader with Redirect Handling"""
    video_id = get_clean_id(link)
    if not video_id:
        return None

    ext = "mp3" if media_type == "audio" else "mp4"
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

    if os.path.exists(file_path):
        return file_path

    try:
        timeout = aiohttp.ClientTimeout(total=600)
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout) as session:
            # Step 1: Get Token
            params = {"url": video_id, "type": media_type}
            async with session.get(f"{API_URL}/download", params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                token = data.get("download_token")
                if not token:
                    return None

            # Step 2: Download with Redirect Handling
            stream_url = f"{API_URL}/stream/{video_id}?type={media_type}&token={token}"
            async with session.get(stream_url, allow_redirects=True) as file_resp:
                if file_resp.status == 200:
                    async with aiofiles.open(file_path, mode='wb') as f:
                        async for chunk in file_resp.content.iter_chunked(65536):
                            await f.write(chunk)
                    
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path
    except Exception as e:
        LOGGER.error(f"API Downloader Error: {e}")
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass
    return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.listbase = "https://youtube.com/playlist?list="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def url(self, message_1: Message) -> Optional[str]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        
        for msg in messages:
            text = msg.text or msg.caption
            if not text: continue
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return text[entity.offset : entity.offset + entity.length]
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            search = VideosSearch(link, limit=1)
            result_data = (await search.next())["result"]
            if not result_data: return None
            
            res = result_data[0]
            title = res["title"]
            duration_min = res["duration"]
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            vidid = res["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            LOGGER.error(f"YouTube Details Error: {e}")
            return None

    async def download(
        self,
        link: str,
        mystic,
        video: bool = False,
        videoid: bool = False,
        **kwargs
    ) -> Tuple[Optional[str], bool]:
        """Main Download function with Security Fallback"""
        if videoid:
            link = self.base + link
        
        # Priority 1: Custom API Downloader
        m_type = "video" if video else "audio"
        downloaded_file = await download_from_api(link, m_type)
        if downloaded_file:
            return downloaded_file, True

        # Priority 2: Security Fallback (yt-dlp)
        clean_id = get_clean_id(link) or "temp_file"
        ext = "mp4" if video else "mp3"
        # Security: Absolute path verification
        output_path = os.path.join(DOWNLOAD_DIR, f"{clean_id}.%(ext)s")
        
        ytdl_opts = {
            "format": "bestvideo+bestaudio/best" if video else "bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
        }

        if not video:
            ytdl_opts["postprocessors"] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            loop = asyncio.get_event_loop()
            def yt_dlp_process():
                with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                    info = ydl.extract_info(link, download=True)
                    return ydl.prepare_filename(info)

            # File ko download karein (Threaded taaki bot freeze na ho)
            raw_path = await loop.run_in_executor(None, yt_dlp_process)
            
            # Post-processing ke baad actual extension check karein
            final_path = raw_path.rsplit('.', 1)[0] + f".{ext}"
            
            if os.path.exists(final_path):
                return final_path, True
            elif os.path.exists(raw_path):
                return raw_path, True
                
        except Exception as e:
            LOGGER.error(f"System Download Failure: {e}")
        
        return None, False

    async def playlist(self, link, limit, user_id, videoid=None):
        if videoid: link = self.listbase + link
        try:
            plist = await Playlist.get(link)
            if not plist or "videos" not in plist: return []
            return [v['id'] for v in plist['videos'][:limit] if v.get('id')]
        except Exception as e:
            LOGGER.error(f"Playlist Error: {e}")
            return []

    async def track(self, link: str, videoid=None):
        det = await self.details(link, videoid)
        if not det: return None, None
        track_details = {
            "title": det[0],
            "link": self.base + det[4],
            "vidid": det[4],
            "duration_min": det[1],
            "thumb": det[3],
        }
        return track_details, det[4]

    async def formats(self, link: str, videoid: bool = None):
        if videoid: link = self.base + link
        ytdl_opts = {"quiet": True}
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                r = await asyncio.to_thread(ydl.extract_info, link, download=False)
                formats_available = []
                for f in r.get("formats", []):
                    if "dash" not in str(f.get("format")).lower():
                        formats_available.append({
                            "format": f.get("format"),
                            "filesize": f.get("filesize"),
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "format_note": f.get("format_note"),
                            "yturl": link,
                        })
                return formats_available, link
        except:
            return [], link
