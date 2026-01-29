# File: usually placed in VIPMUSIC/utils/youtube.py or helpers/youtube.py
# Make sure this file is the one actually being imported

import asyncio
import glob
import os
import random
import re
from typing import Union, Tuple, Optional, Dict, Any

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config
from VIPMUSIC import LOGGER

logger = LOGGER(__name__)

# ─── API Key Rotation ───────────────────────────────────────
API_KEYS = [k.strip() for k in config.API_KEY.split(",") if k.strip()]
current_api_key_index = 0


def get_youtube_client():
    global current_api_key_index
    if current_api_key_index >= len(API_KEYS):
        return None
    return build(
        "youtube", "v3",
        developerKey=API_KEYS[current_api_key_index],
        static_discovery=False
    )


def switch_to_next_api_key() -> bool:
    global current_api_key_index
    current_api_key_index += 1
    if current_api_key_index < len(API_KEYS):
        logger.warning(f"Quota exceeded → switching to API key #{current_api_key_index + 1}")
        return True
    logger.error("All YouTube API keys exhausted!")
    return False


# ─── Cookie Helpers ─────────────────────────────────────────
def pick_random_cookie_file() -> Optional[str]:
    try:
        cookie_dir = os.path.join(os.getcwd(), "cookies")
        cookie_files = glob.glob(os.path.join(cookie_dir, "*.txt"))
        if not cookie_files:
            return None
        return random.choice(cookie_files)
    except Exception:
        return None


class YouTubeAPI:
    def __init__(self):
        self.base_url = "https://www.youtube.com/watch?v="
        self.playlist_base = "https://www.youtube.com/playlist?list="
        self.url_pattern = r"(?:youtube\.com|youtu\.be)"

    @staticmethod
    def parse_iso_duration(iso_duration: str) -> Tuple[str, int]:
        """ PT5M30S → "05:30", 330 """
        if not iso_duration:
            return "00:00", 0

        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(iso_duration)
        if not match:
            return "00:00", 0

        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)

        total_seconds = h * 3600 + m * 60 + s
        time_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        return time_str, total_seconds

    # ─── THIS IS THE METHOD YOUR CODE IS CALLING ────────────────────────────────
    async def url(self, message: Message) -> Optional[str]:
        """
        Extract YouTube link from message (entities or caption links)
        This method MUST exist because play.py calls: await YouTube.url(message)
        """
        messages_to_check = [message]
        if message.reply_to_message:
            messages_to_check.append(message.reply_to_message)

        for msg in messages_to_check:
            # Regular URL entities (blue text links)
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption or ""
                        return text[entity.offset : entity.offset + entity.length]

            # Text links in captions (clickable links)
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        return None

    async def exists(self, link: str, videoid: Union[bool, str] = False) -> bool:
        if videoid:
            link = self.base_url + str(link)
        return bool(re.search(self.url_pattern, link, re.IGNORECASE))

    async def get_video_details(
        self,
        query_or_url_or_id: str,
        is_videoid: Union[bool, str] = False
    ) -> Optional[Tuple[str, str, int, str, str]]:
        """ Returns: (title, duration_str, duration_sec, thumbnail_url, video_id) """

        if is_videoid:
            video_id = str(query_or_url_or_id)
        else:
            m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", query_or_url_or_id)
            video_id = m.group(1) if m else None

        while True:
            yt = get_youtube_client()
            if not yt:
                return None

            try:
                if not video_id:
                    res = await asyncio.to_thread(
                        yt.search().list(
                            q=query_or_url_or_id,
                            part="id",
                            maxResults=1,
                            type="video"
                        ).execute()
                    )
                    if not res.get("items"):
                        return None
                    video_id = res["items"][0]["id"]["videoId"]

                data = await asyncio.to_thread(
                    yt.videos().list(
                        part="snippet,contentDetails",
                        id=video_id
                    ).execute()
                )

                if not data.get("items"):
                    return None

                item = data["items"][0]
                title = item["snippet"]["title"]
                thumb = item["snippet"]["thumbnails"].get("high", {}).get("url", "")
                dur_str, dur_sec = self.parse_iso_duration(item["contentDetails"]["duration"])

                return title, dur_str, dur_sec, thumb, video_id

            except HttpError as e:
                if e.resp.status == 403 and switch_to_next_api_key():
                    continue
                logger.exception("YouTube API error")
                return None

    async def download(
        self,
        url_or_id: str,
        is_videoid: Union[bool, str] = False,
        songaudio: bool = False,
        songvideo: bool = False,
        format_id: Optional[str] = None,
        custom_title: Optional[str] = None
    ) -> Tuple[Optional[str], bool]:
        if is_videoid:
            url = self.base_url + str(url_or_id)
        else:
            url = url_or_id

        os.makedirs("downloads", exist_ok=True)

        cookie = pick_random_cookie_file()
        common = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }
        if cookie:
            common["cookiefile"] = cookie

        def run_ytdl(opts):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info), True
            except Exception as e:
                logger.exception(f"yt-dlp error: {e}")
                return None, False

        loop = asyncio.get_running_loop()

        if songvideo:
            title = (custom_title or "video").replace("/", "_").replace("\\", "_")
            opts = {
                **common,
                "format": f"{format_id}+bestaudio/best" if format_id else "bestvideo[height<=?720]+bestaudio/best",
                "outtmpl": f"downloads/{title}.%(ext)s",
                "merge_output_format": "mp4",
            }
            return await loop.run_in_executor(None, lambda: run_ytdl(opts))

        if songaudio:
            title = (custom_title or "audio").replace("/", "_").replace("\\", "_")
            opts = {
                **common,
                "format": "ba[ext=m4a]/bestaudio/best",
                "outtmpl": f"downloads/{title}.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "continuedl": True,
                "retries": 10,
            }
            return await loop.run_in_executor(None, lambda: run_ytdl(opts))

        # default audio
        opts = {
            **common,
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
        }
        return await loop.run_in_executor(None, lambda: run_ytdl(opts))


# Usually in your main file or __init__ you do:
# YouTube = YouTubeAPI()
