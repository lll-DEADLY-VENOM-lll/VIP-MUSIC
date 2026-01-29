import asyncio
import glob
import json
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

# API KEY ROTATION
API_KEYS = [k.strip() for k in config.API_KEY.split(",") if k.strip()]
current_key_index = 0

def get_youtube_client():
    global current_key_index
    if current_key_index >= len(API_KEYS):
        logger.error("Sab YouTube API keys khatam!")
        return None
    # cache_discovery=False → warning suppress karega
    return build("youtube", "v3", developerKey=API_KEYS[current_key_index],
                 cache_discovery=False, static_discovery=False)

def switch_key():
    global current_key_index
    current_key_index += 1
    if current_key_index < len(API_KEYS):
        logger.warning(f"Switching to API Key #{current_key_index + 1}")
        return True
    logger.error("All keys exhausted!")
    return False

def get_cookie_file():
    try:
        folder = os.path.join(os.getcwd(), "cookies")
        txt_files = glob.glob(os.path.join(folder, '*.txt'))
        if not txt_files:
            return None
        cookie = random.choice(txt_files)
        logger.info(f"Using cookie: {cookie}")
        return cookie
    except Exception:
        return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    def parse_duration(self, duration: str):
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration or "")
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        total = h * 3600 + m * 60 + s
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}", total

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message, message.reply_to_message] if message.reply_to_message else [message]
        for msg in messages:
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return (msg.text or msg.caption)[entity.offset:entity.offset + entity.length]
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        vidid = link if videoid else re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link).group(1) if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link) else None
        while True:
            youtube = get_youtube_client()
            if not youtube: return None
            try:
                if not vidid:
                    search = await asyncio.to_thread(youtube.search().list(q=link, part="id", maxResults=1, type="video").execute)
                    if not search.get("items"): return None
                    vidid = search["items"][0]["id"]["videoId"]
                
                data = await asyncio.to_thread(youtube.videos().list(part="snippet,contentDetails", id=vidid).execute)
                if not data.get("items"): return None
                item = data["items"][0]
                title = item["snippet"]["title"]
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
                dur_str, dur_sec = self.parse_duration(item["contentDetails"]["duration"])
                return title, dur_str, dur_sec, thumb, vidid
            except HttpError as e:
                if e.resp.status == 403 and switch_key(): continue
                logger.error(f"API error: {e}")
                return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        if not res: return None, None
        title, d_min, d_sec, thumb, vidid = res
        return {"title": title, "link": self.base + vidid, "vidid": vidid, "duration_min": d_min, "thumb": thumb}, vidid

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        while True:
            youtube = get_youtube_client()
            if not youtube: return None
            try:
                search = await asyncio.to_thread(youtube.search().list(q=link, part="snippet", maxResults=10, type="video").execute)
                if not search.get("items"): return None
                item = search["items"][query_type % len(search["items"])]
                vidid = item["id"]["videoId"]
                title = item["snippet"]["title"]
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
                vd = await asyncio.to_thread(youtube.videos().list(part="contentDetails", id=vidid).execute)
                d_min, _ = self.parse_duration(vd["items"][0]["contentDetails"]["duration"])
                return title, d_min, thumb, vidid
            except HttpError as e:
                if e.resp.status == 403 and switch_key(): continue
                return None

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        cookie = get_cookie_file()
        cookie_arg = f"--cookies {cookie}" if cookie else ""
        cmd = f'yt-dlp {cookie_arg} -i --get-id --flat-playlist --playlist-end {limit} --skip-download "{link}"'
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        return [k.strip() for k in stdout.decode().splitlines() if k.strip()]

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None):
        if videoid: link = self.base + videoid

        loop = asyncio.get_running_loop()
        cookie = get_cookie_file()

        common_opts = {
            "quiet": False,
            "verbose": True,               # ← full yt-dlp logs terminal pe
            "no_warnings": False,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "continuedl": True,
            "retries": 10,
            "noplaylist": True,
        }
        if cookie:
            common_opts["cookiefile"] = cookie
            print(f"[COOKIE] → {cookie}")

        os.makedirs("downloads", exist_ok=True)

        try:
            if songvideo:
                print(f"[VIDEO DOWNLOAD] {title}")
                opts = {
                    **common_opts,
                    "format": f"{format_id}+bestaudio/best" if format_id else "bestvideo[height<=?720]+bestaudio/best",
                    "outtmpl": f"downloads/{title} - %(id)s.%(ext)s",
                    "merge_output_format": "mp4",
                }
            elif songaudio:
                print(f"[AUDIO DOWNLOAD] {title}")
                opts = {
                    **common_opts,
                    "format": "bestaudio/best",
                    "outtmpl": f"downloads/{title} - %(id)s.%(ext)s",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }
            else:
                print("[DEFAULT AUDIO DOWNLOAD]")
                opts = {
                    **common_opts,
                    "format": "bestaudio/best",
                    "outtmpl": "downloads/%(title)s - %(id)s.%(ext)s",
                }

            def run_ytdl():
                print("[YT-DLP VERSION]:", yt_dlp.version.__version__)
                print("[OPTIONS]:", json.dumps(opts, indent=2, default=str))
                print(f"[LINK]: {link}")

                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(link, download=True)
                    filename = ydl.prepare_filename(info)
                    print(f"[FILE SAVED]: {filename}")
                    if os.path.exists(filename):
                        size = os.path.getsize(filename) / (1024 * 1024)
                        print(f"[SIZE]: {size:.2f} MB")
                    return filename

            file_path = await loop.run_in_executor(None, run_ydl)

            if file_path and os.path.exists(file_path):
                print(f"[SUCCESS] → {file_path}")
                return file_path, True
            print("[FAIL] File not found on disk!")
            return None, False

        except Exception as ex:
            print("[DOWNLOAD CRASH]")
            import traceback
            traceback.print_exc()
            logger.exception("Download failed")
            return None, False
