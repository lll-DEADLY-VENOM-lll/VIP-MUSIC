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
from AnonMusic import LOGGER
from AnonMusic.utils.formatters import time_to_seconds

logger = LOGGER(__name__)

# --- API SEQUENTIAL ROTATION LOGIC ---
API_KEYS = [k.strip() for k in config.API_KEY.split(",")]
current_key_index = 0

def get_youtube_client():
    global current_key_index
    if current_key_index >= len(API_KEYS):
        return None
    try:
        return build("youtube", "v3", developerKey=API_KEYS[current_key_index], static_discovery=False)
    except Exception as e:
        logger.error(f"Error creating client for key #{current_key_index + 1}: {e}")
        return None

def switch_key():
    global current_key_index
    current_key_index += 1
    if current_key_index < len(API_KEYS):
        logger.warning(f"YouTube Quota Finished. Switching to Key #{current_key_index + 1}")
        return True
    logger.error("All YouTube API Keys are exhausted!")
    return False

# --- COOKIE LOGIC ---
def get_cookie_file():
    folder_path = f"{os.getcwd()}/cookies"
    if not os.path.exists(folder_path):
        return None
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    def extract_id(self, url):
        if not url or "None" in str(url): return None
        match = re.search(r"(?:v=|\/|embed\/|youtu.be\/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None

    def parse_duration(self, duration):
        """ISO 8601 duration conversion (PT5M30S -> 05:30)"""
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match: return "00:00", 0
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        total_seconds = h * 3600 + m * 60 + s
        if h > 0:
            duration_str = f"{h}:{m:02d}:{s:02d}"
        else:
            duration_str = f"{m}:{s:02d}"
        return duration_str, total_seconds

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message, message.reply_to_message] if message.reply_to_message else [message]
        for msg in messages:
            if not msg: continue
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return (msg.text or msg.caption)[entity.offset : entity.offset + entity.length]
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        vidid = link if (videoid and link != "None") else self.extract_id(link)
        
        while True:
            youtube = get_youtube_client()
            if not youtube: break # Exhausted keys

            try:
                # Agar ID nahi mili toh pehle search karein
                if not vidid or vidid == "None":
                    search = await asyncio.to_thread(youtube.search().list(q=link, part="id", maxResults=1, type="video").execute)
                    if not search.get("items"): return None
                    vidid = search["items"][0]["id"]["videoId"]
                
                # Metadata fetch
                video_data = await asyncio.to_thread(youtube.videos().list(part="snippet,contentDetails", id=vidid).execute)
                if not video_data.get("items"): return None
                
                item = video_data["items"][0]
                title = item["snippet"]["title"]
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
                d_min, d_sec = self.parse_duration(item["contentDetails"]["duration"])
                return title, d_min, d_sec, thumb, vidid

            except HttpError as e:
                if e.resp.status in [403, 429] and switch_key():
                    continue
                break
            except Exception:
                break
        
        # Method 2: Fallback to yt-dlp if API fails
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(link if not videoid else self.base + link, download=False))
                return info['title'], f"{info['duration']//60}:{info['duration']%60:02d}", info['duration'], info.get('thumbnail'), info['id']
        except: return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        if not res:
            # Placeholder to avoid KeyError 'link'
            return {
                "title": "Unknown Track",
                "link": link or "https://youtube.com",
                "vidid": "None",
                "duration_min": "00:00",
                "thumb": None
            }, None
        
        title, d_min, d_sec, thumb, vidid = res
        track_details = {
            "title": title,
            "link": self.base + vidid,
            "vidid": vidid,
            "duration_min": d_min,
            "thumb": thumb
        }
        return track_details, vidid

    async def video(self, link: str, videoid: Union[bool, str] = None):
        vid = link if videoid else self.extract_id(link)
        if not vid or vid == "None": return 0, "Invalid ID"
        
        full_link = self.base + vid
        cookie = get_cookie_file()
        opts = ["yt-dlp", "-g", "-f", "best[height<=?720]", "--geo-bypass", full_link]
        if cookie: opts.extend(["--cookies", cookie])
        
        proc = await asyncio.create_subprocess_exec(*opts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, stderr.decode())

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        p_link = self.listbase + link if videoid else link
        cookie = get_cookie_file()
        cookie_arg = f"--cookies {cookie}" if cookie else ""
        cmd = f"yt-dlp {cookie_arg} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {p_link}"
        playlist = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await playlist.communicate()
        return [k.strip() for k in stdout.decode().split("\n") if k.strip() and k.strip() != "None"]

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        while True:
            youtube = get_youtube_client()
            if not youtube: break
            try:
                search = await asyncio.to_thread(youtube.search().list(q=link, part="id,snippet", maxResults=10, type="video").execute)
                items = search.get("items", [])
                if not items or len(items) <= query_type: return None
                
                selected = items[query_type]
                vidid = selected["id"]["videoId"]
                return await self.details(vidid, videoid=True)
            except HttpError as e:
                if e.resp.status in [403, 429] and switch_key(): continue
                break
        return None

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None):
        vid = link if videoid else self.extract_id(link)
        if not vid or vid == "None": return None
        
        full_link = self.base + vid
        loop = asyncio.get_running_loop()
        cookie = get_cookie_file()
        
        common_opts = {"quiet": True, "no_warnings": True, "geo_bypass": True, "nocheckcertificate": True}
        if cookie: common_opts["cookiefile"] = cookie

        def ytdl_run(opts):
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(full_link, download=True)
                return ydl.prepare_filename(info)

        if songvideo:
            opts = {**common_opts, "format": f"{format_id}+140/best", "outtmpl": f"downloads/{title}.%(ext)s", "merge_output_format": "mp4"}
        elif songaudio:
            opts = {**common_opts, "format": "bestaudio/best", "outtmpl": f"downloads/{title}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}
        else:
            opts = {**common_opts, "format": "bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s"}

        try:
            downloaded_file = await loop.run_in_executor(None, lambda: ytdl_run(opts))
            return downloaded_file, True
        except: return None

    # Extra compatibility helpers
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        return bool(videoid or re.search(self.regex, link))
