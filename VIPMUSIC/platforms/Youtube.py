import asyncio
import glob
import os
import random
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError

import config
from VIPMUSIC import LOGGER
from VIPMUSIC.utils.formatters import time_to_seconds

logger = LOGGER(__name__)

# --- API ROTATION ---
API_KEYS = [k.strip() for k in config.API_KEY.split(",")]
current_key_index = 0

def get_youtube_client():
    global current_key_index
    if current_key_index >= len(API_KEYS): return None
    try:
        return build("youtube", "v3", developerKey=API_KEYS[current_key_index], static_discovery=False)
    except: return None

def switch_key():
    global current_key_index
    current_key_index += 1
    return current_key_index < len(API_KEYS)

# --- CENTRALIZED YTDL OPTIONS ---
def get_ytdl_opts(custom_opts=None):
    folder_path = f"{os.getcwd()}/cookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    cookie_file = random.choice(txt_files) if txt_files else None

    opts = {
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    if os.getenv("TOKEN_ALLOW") == "True":
        opts.update({"username": "oauth2", "password": ""})
    elif cookie_file:
        opts["cookiefile"] = cookie_file
        
    if custom_opts:
        opts.update(custom_opts)
    return opts

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    def extract_id(self, url):
        if not url or "None" in str(url): return None
        match = re.search(r"(?:v=|\/|embed\/|youtu.be\/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None

    def parse_duration(self, duration):
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match: return "00:00", 0
        h, m, s = [int(match.group(i) or 0) for i in range(1, 4)]
        total = h * 3600 + m * 60 + s
        return (f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"), total

    async def url(self, message: Message):
        msgs = [message, message.reply_to_message] if message.reply_to_message else [message]
        for m in msgs:
            if not m: continue
            if m.entities:
                for e in m.entities:
                    if e.type == MessageEntityType.URL:
                        return (m.text or m.caption)[e.offset : e.offset + e.length]
            if m.caption_entities:
                for e in m.caption_entities:
                    if e.type == MessageEntityType.TEXT_LINK: return e.url
        return None

    async def details(self, link: str, videoid=None):
        vid = link if (videoid and link != "None") else self.extract_id(link)
        while True:
            client = get_youtube_client()
            if not client: break
            try:
                if not vid or vid == "None":
                    search = await asyncio.to_thread(client.search().list(q=link, part="id", maxResults=1, type="video").execute)
                    if not search.get("items"): return None
                    vid = search["items"][0]["id"]["videoId"]
                
                res = await asyncio.to_thread(client.videos().list(part="snippet,contentDetails", id=vid).execute)
                if not res.get("items"): return None
                item = res["items"][0]
                d_min, d_sec = self.parse_duration(item["contentDetails"]["duration"])
                return item["snippet"]["title"], d_min, d_sec, item["snippet"]["thumbnails"]["high"]["url"], vid
            except HttpError as e:
                if e.resp.status in [403, 429] and switch_key(): continue
                break
            except: break

        # Fallback to yt-dlp
        try:
            with yt_dlp.YoutubeDL(get_ytdl_opts()) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, link if not videoid else self.base + vid, download=False)
                return info['title'], f"{info['duration']//60}:{info['duration']%60:02d}", info['duration'], info.get('thumbnail'), info['id']
        except: return None

    async def track(self, link: str, videoid=None):
        res = await self.details(link, videoid)
        if not res:
            return {"title": "Unknown", "link": link or self.base, "vidid": "None", "duration_min": "00:00", "thumb": None}, None
        return {"title": res[0], "link": self.base + res[4], "vidid": res[4], "duration_min": res[1], "thumb": res[3]}, res[4]

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None):
        vid = link if videoid else self.extract_id(link)
        if not vid or vid == "None": 
            logger.error("Download failed: Invalid Video ID")
            return None
        
        full_link = self.base + vid
        loop = asyncio.get_running_loop()

        # Download settings
        if songvideo:
            opts = get_ytdl_opts({"format": f"{format_id}+140/best", "outtmpl": f"downloads/{title}.%(ext)s", "merge_output_format": "mp4"})
        elif songaudio:
            opts = get_ytdl_opts({"format": "bestaudio/best", "outtmpl": f"downloads/{title}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]})
        else:
            opts = get_ytdl_opts({"format": "bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s"})

        def run_dl():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(full_link, download=True)
                return ydl.prepare_filename(info)

        try:
            downloaded_file = await loop.run_in_executor(None, run_dl)
            return downloaded_file, True
        except Exception as e:
            logger.error(f"Download Error: {str(e)}")
            # Last resort fallback: try getting direct URL without downloading
            try:
                with yt_dlp.YoutubeDL(get_ytdl_opts()) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, full_link, download=False)
                    return info['url'], False # False means direct link, not file path
            except:
                return None

    async def playlist(self, link, limit, user_id, videoid=None):
        p_link = f"https://youtube.com/playlist?list={link}" if videoid else link
        try:
            with yt_dlp.YoutubeDL(get_ytdl_opts({"extract_flat": True, "playlistend": int(limit)})) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, p_link, download=False)
                return [item['id'] for item in info['entries'] if item]
        except: return []

    async def slider(self, link: str, query_type: int, videoid=None):
        client = get_youtube_client()
        if not client: return None
        try:
            res = await asyncio.to_thread(client.search().list(q=link, part="id", maxResults=10, type="video").execute)
            return await self.details(res["items"][query_type]["id"]["videoId"], videoid=True)
        except: return None
