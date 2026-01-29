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

# --- API KEY ROTATION ---
API_KEYS = [k.strip() for k in config.API_KEY.split(",")]
current_key_index = 0

def get_youtube_client():
    global current_key_index
    if current_key_index >= len(API_KEYS):
        return None
    return build("youtube", "v3", developerKey=API_KEYS[current_key_index], static_discovery=False)

def switch_key():
    global current_key_index
    current_key_index += 1
    if current_key_index < len(API_KEYS):
        logger.warning(f"YouTube Quota Finished. Switching to Key #{current_key_index + 1}")
        return True
    return False

# --- COOKIE LOGIC ---
def get_cookie_file():
    folder_path = os.path.join(os.getcwd(), "cookies")
    if not os.path.exists(folder_path):
        return None
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    def parse_duration(self, duration):
        if not duration: return "00:00", 0
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        total_seconds = h * 3600 + m * 60 + s
        duration_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        return duration_str, total_seconds

    # --- YE METHOD MISSING THA ---
    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        for msg in messages:
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return (msg.text or msg.caption)[entity.offset : entity.offset + entity.length]
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: 
            vidid = link
        else:
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None

        while True:
            youtube = get_youtube_client()
            if not youtube: break
            try:
                if not vidid:
                    search = await asyncio.to_thread(youtube.search().list(q=link, part="id", maxResults=1, type="video").execute)
                    if not search.get("items"): return None
                    vidid = search["items"][0]["id"]["videoId"]
                
                video_data = await asyncio.to_thread(youtube.videos().list(part="snippet,contentDetails", id=vidid).execute)
                if not video_data.get("items"): return None
                
                item = video_data["items"][0]
                title = item["snippet"]["title"]
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
                d_min, d_sec = self.parse_duration(item["contentDetails"]["duration"])
                return title, d_min, d_sec, thumb, vidid
            except HttpError as e:
                if e.resp.status == 403 and switch_key(): continue
                break

        # API Fail Fallback to yt-dlp
        try:
            opts = {"quiet": True, "no_warnings": True, "cookiefile": get_cookie_file()}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, f"ytsearch1:{link}" if not vidid else vidid, download=False)
                if 'entries' in info: info = info['entries'][0]
                return info['title'], str(info.get('duration')), info.get('duration'), info.get('thumbnail'), info['id']
        except: return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        if not res: return None, None
        title, d_min, d_sec, thumb, vidid = res
        return {"title": title, "link": self.base + vidid, "vidid": vidid, "duration_min": d_min, "thumb": thumb}, vidid

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        cookie = get_cookie_file()
        # Fixed 403 & No VPlay (Only Audio)
        opts = [
            "yt-dlp", "-g", "-f", "bestaudio", 
            "--geo-bypass", "--no-check-certificate", 
            "--user-agent", random.choice(self.user_agents),
            link
        ]
        if cookie: opts.extend(["--cookies", cookie])
        
        proc = await asyncio.create_subprocess_exec(*opts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, stderr.decode())

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        cookie = get_cookie_file()
        cookie_arg = f"--cookies {cookie}" if cookie else ""
        cmd = f"yt-dlp {cookie_arg} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        playlist = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await playlist.communicate()
        return [k.strip() for k in stdout.decode().split("\n") if k.strip()]

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        cookie = get_cookie_file()
        
        common_opts = {
            "quiet": True, "no_warnings": True, "geo_bypass": True, 
            "nocheckcertificate": True, "cookiefile": cookie,
            "user_agent": random.choice(self.user_agents),
            "source_address": "0.0.0.0" # Force IPv4 to avoid 403
        }

        if songvideo:
            opts = {**common_opts, "format": f"{format_id}+140/bestvideo+bestaudio", "outtmpl": f"downloads/{title}.%(ext)s", "merge_output_format": "mp4"}
        else:
            opts = {**common_opts, "format": "bestaudio/best", "outtmpl": f"downloads/{title}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}

        def ytdl_run():
            # Try multiple clients to avoid 403 Forbidden
            for client in ["android", "ios", "web"]:
                try:
                    opts["extractor_args"] = {"youtube": {"player_client": [client]}}
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(link, download=True)
                        return ydl.prepare_filename(info)
                except: continue
            raise Exception("Download failed on all clients")

        try:
            downloaded_file = await loop.run_in_executor(None, ytdl_run)
            return downloaded_file, True
        except Exception as e:
            return str(e), False
