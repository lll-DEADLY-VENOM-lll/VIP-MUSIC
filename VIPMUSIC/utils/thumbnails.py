#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License .
#

from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

async def gen_thumb(videoid):
    try:
        query = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(query, limit=1)
        res = await results.next()
        for result in res["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail
    except Exception:
        return YOUTUBE_IMG_URL

async def gen_qthumb(vidid):
    try:
        query = f"https://www.youtube.com/watch?v={vidid}"
        results = VideosSearch(query, limit=1)
        res = await results.next()
        for result in res["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail
    except Exception:
        return YOUTUBE_IMG_URL

# Yeh niche wale functions bhi add kar diye hain taaki koi aur error na aaye
async def get_thumb(videoid):
    return await gen_thumb(videoid)
