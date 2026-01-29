import asyncio
import os
import re
import random
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError

import config
from VIPMUSIC.utils.formatters import time_to_seconds

# --- API ROTATION LOGIC ---
API_KEYS = [k.strip() for k in config.API_KEY.split(",")]
current_key_index = 0

def get_youtube_client():
    global current_key_index
    selected_key = API_KEYS[current_key_index]
    return build("youtube", "v3", developerKey=selected_key, static_discovery=False)

def rotate_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)

# --- लेटेस्ट YT-DLP 403 BYPASS SETTINGS ---
# YouTube अब 'Web' क्लाइंट को ब्लॉक कर रहा है, इसलिए हम 'Android' क्लाइंट का उपयोग करेंगे।
YTDL_OPTIONS = {
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "format": "bestaudio/best",
    "user_agent": "com.google.android.youtube/19.29.37 (Linux; U; Android 11; en_US) gzip", # Mobile User-Agent
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "ios"], # सबसे जरूरी: Web को छोड़कर Mobile Client यूज़ करना
            "skip": ["dash", "hls"]
        }
    },
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

cookie_txt_file = "VIPMUSIC/cookies.txt"
if os.path.exists(cookie_txt_file):
    YTDL_OPTIONS["cookiefile"] = cookie_txt_file

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def details(self, link: str, videoid: Union[bool, str] = None, retry_count=0):
        if retry_count >= len(API_KEYS): return None
        
        # Extract Video ID
        if videoid: vidid = link
        else:
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None
        
        youtube = get_youtube_client()
        try:
            if not vidid:
                search = await asyncio.to_thread(youtube.search().list(q=link, part="id", maxResults=1, type="video").execute)
                if not search.get("items"): return None
                vidid = search["items"][0]["id"]["videoId"]
            
            video_resp = await asyncio.to_thread(youtube.videos().list(part="snippet,contentDetails", id=vidid).execute)
            if not video_resp.get("items"): return None
            
            item = video_resp["items"][0]
            title = item["snippet"]["title"]
            thumb = item["snippet"]["thumbnails"]["high"]["url"]
            
            # Duration Parsing
            dur = item["contentDetails"]["duration"]
            match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', dur)
            h, m, s = [int(match.group(i) or 0) for i in range(1, 4)]
            d_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
            
            return title, d_str, thumb, vidid
        except HttpError as e:
            if e.resp.status in [403, 429]:
                rotate_api_key()
                return await self.details(link, videoid, retry_count + 1)
            return None

    # --- 403 FORBIDDEN FIX FOR VIDEO DOWNLOAD ---
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        
        # Command with new bypass arguments
        cmd = [
            "yt-dlp",
            "-g",
            "-f", "best[height<=?480][ext=mp4]/best",
            "--extractor-args", "youtube:player_client=android",
            "--user-agent", YTDL_OPTIONS["user_agent"],
            "--no-playlist",
            link
        ]
        
        if os.path.exists(cookie_txt_file):
            cmd.extend(["--cookies", cookie_txt_file])

        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        
        if stdout:
            return (1, stdout.decode().split("\n")[0])
        else:
            err = stderr.decode()
            print(f"DEBUG: Video fail: {err}")
            return (0, err)

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()

        def dl_logic():
            opts = YTDL_OPTIONS.copy()
            if songvideo:
                opts.update({"format": f"{format_id}+140/best", "merge_output_format": "mp4", "outtmpl": f"downloads/{title}.%(ext)s"})
            elif songaudio:
                opts.update({"format": format_id if format_id else "bestaudio/best", "outtmpl": f"downloads/{title}.%(ext)s"})
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return ydl.prepare_filename(info)

        try:
            result = await loop.run_in_executor(None, dl_logic)
            return (result, True) if (songaudio or songvideo) else result
        except Exception as e:
            print(f"Download Error: {e}")
            return None

    # Helper methods call details
    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[0] if res else "Unknown"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[2] if res else None
