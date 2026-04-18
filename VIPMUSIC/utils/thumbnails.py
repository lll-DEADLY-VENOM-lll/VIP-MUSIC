#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github
# Cleaned and Optimized version
#FUCK YOU

from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid):
    """
    YouTube Video ID se official thumbnail nikalne ke liye.
    Ismein search library ka use kiya gaya hai.
    """
    try:
        query = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(query, limit=1)
        res = await results.next()
        
        if res["result"]:
            # Pehla result ka high resolution thumbnail nikalna
            thumbnail = res["result"][0]["thumbnails"][0]["url"].split("?")[0]
            return thumbnail
        return YOUTUBE_IMG_URL
    except Exception:
        return YOUTUBE_IMG_URL

# Agar aapko fast kaam chahiye bina search kiye:
def get_official_thumb(videoid):
    """
    Direct YouTube server se high quality thumbnail link generate karne ke liye (Fastest Method)
    """
    return f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
