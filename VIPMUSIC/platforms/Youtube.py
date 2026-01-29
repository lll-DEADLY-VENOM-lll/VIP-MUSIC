import asyncio
import glob
import os
import random
import re
from typing import Union
from googleapiclient.discovery import build
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from yt_dlp import YoutubeDL

import config
from VIPMUSIC.utils.database import is_on_off
from VIPMUSIC.utils.formatters import time_to_seconds

# YouTube API Configuration
YOUTUBE_API_SERVICE_NAME = "AIzaSyCi7cuAr68B3xPxeXueL5ctrohUKN9vOkI"
YOUTUBE_API_VERSION = "v3"

# API Client Initialization
def get_youtube_client():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=config.API_KEY)

def parse_duration(duration):
    """YouTube ISO 8601 duration (PT5M30S) ko seconds aur string mein convert karta hai"""
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)
    if not match:
        return 0, "00:00"
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    if hours > 0:
        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        duration_str = f"{minutes}:{seconds:02d}"
    return total_seconds, duration_str

def cookies():
    folder_path = f"{os.getcwd()}/cookies"
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        return None
    cookie_txt_file = random.choice(txt_files)
    return f"cookies/{os.path.basename(cookie_txt_file)}"

def get_ytdl_options(ytdl_opts, commamdline=True) -> Union[str, dict, list]:
    cookie_file = cookies()
    if commamdline:
        if isinstance(ytdl_opts, list):
            if os.getenv("TOKEN_ALLOW") == "True":
                ytdl_opts += ["--username", "oauth2", "--password", "''"]
            elif cookie_file:
                ytdl_opts += ["--cookies", cookie_file]
    else:
        if isinstance(ytdl_opts, dict):
            if os.getenv("TOKEN_ALLOW") == "True":
                ytdl_opts.update({"username": "oauth2", "password": ""})
            elif cookie_file:
                ytdl_opts["cookiefile"] = cookie_file
    return ytdl_opts

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.client = get_youtube_client()

    def extract_id(self, url):
        pattern = r"(?:v=|\/|embed\/|youtu.be\/)([0-9A-Za-z_-]{11})"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            return True
        if re.search(self.regex, link):
            return True
        return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if not videoid:
            videoid = self.extract_id(link)
        
        loop = asyncio.get_event_loop()
        # API Call
        search_response = await loop.run_in_executor(None, lambda: self.client.videos().list(
            part="snippet,contentDetails",
            id=videoid
        ).execute())

        if not search_response["items"]:
            return None

        item = search_response["items"][0]
        title = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
        duration_iso = item["contentDetails"]["duration"]
        duration_sec, duration_min = parse_duration(duration_iso)
        
        return title, duration_min, duration_sec, thumbnail, videoid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[0] if res else "Unknown"

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[1] if res else "00:00"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[3] if res else None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        cmd = ["yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", f"{link}"]
        cmd = get_ytdl_options(cmd)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        playlist_id = link.split("list=")[1].split("&")[0] if "list=" in link else link
        loop = asyncio.get_event_loop()
        results = []
        next_page_token = None
        
        while len(results) < int(limit):
            response = await loop.run_in_executor(None, lambda: self.client.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute())
            
            for item in response.get("items", []):
                results.append(item["contentDetails"]["videoId"])
            
            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(results) >= int(limit):
                break
        return results[:int(limit)]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        details = await self.details(link, videoid)
        if not details:
            return None, None
        
        title, duration_min, duration_sec, thumbnail, vidid = details
        track_details = {
            "title": title,
            "link": self.base + vidid,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        ytdl_opts = {"quiet": True}
        ytdl_opts = get_ytdl_options(ytdl_opts, False)
        ydl = YoutubeDL(ytdl_opts)
        
        formats_available = []
        loop = asyncio.get_event_loop()
        r = await loop.run_in_executor(None, lambda: ydl.extract_info(link, download=False))
        
        for f in r["formats"]:
            if "dash" not in str(f.get("format")).lower():
                try:
                    formats_available.append({
                        "format": f.get("format"),
                        "filesize": f.get("filesize"),
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "format_note": f.get("format_note"),
                        "yturl": link,
                    })
                except: continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        # Slider function generally searches for a query
        loop = asyncio.get_event_loop()
        search_response = await loop.run_in_executor(None, lambda: self.client.search().list(
            q=link,
            part="id,snippet",
            maxResults=10,
            type="video"
        ).execute())

        items = search_response.get("items", [])
        if not items: return None
        
        selected = items[query_type]
        vidid = selected["id"]["videoId"]
        # Metadata fetch for duration
        title, duration_min, _, thumbnail, _ = await self.details(vidid, videoid=True)
        return title, duration_min, thumbnail, vidid

    async def download(self, link, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None):
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        def audio_dl():
            opts = {"format": "bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s", "quiet": True}
            opts = get_ytdl_options(opts, False)
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return ydl.prepare_filename(info)

        def video_dl():
            opts = {"format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])", "outtmpl": "downloads/%(id)s.%(ext)s", "quiet": True}
            opts = get_ytdl_options(opts, False)
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return ydl.prepare_filename(info)

        if songvideo:
            fpath = f"downloads/{title}.mp4"
            opts = {"format": f"{format_id}+140", "outtmpl": fpath, "merge_output_format": "mp4", "quiet": True}
            opts = get_ytdl_options(opts, False)
            await loop.run_in_executor(None, lambda: YoutubeDL(opts).download([link]))
            return fpath
        
        elif songaudio:
            fpath = f"downloads/{title}.mp3"
            opts = {
                "format": format_id, 
                "outtmpl": f"downloads/{title}.%(ext)s",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                "quiet": True
            }
            opts = get_ytdl_options(opts, False)
            await loop.run_in_executor(None, lambda: YoutubeDL(opts).download([link]))
            return fpath

        elif video:
            if await is_on_off(config.YTDOWNLOADER):
                return await loop.run_in_executor(None, video_dl), True
            else:
                cmd = ["yt-dlp", "-g", "-f", "best[height<=?720]"]
                cmd = get_ytdl_options(cmd)
                cmd.append(link)
                res = await shell_cmd(" ".join(cmd))
                return res.split("\n")[0], None
        else:
            return await loop.run_in_executor(None, audio_dl), True
