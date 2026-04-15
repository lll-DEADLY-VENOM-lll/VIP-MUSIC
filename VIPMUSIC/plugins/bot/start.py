import asyncio
import random
import time

from py_yt import VideosSearch
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from VIPMUSIC import app
from VIPMUSIC.misc import _boot_
from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
from VIPMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
# FIXED IMPORTS: Standard names used to prevent ImportErrors
from VIPMUSIC.utils.inline import help_panel, private_panel, start_panel
from config import BANNED_USERS, START_IMG_URL
from strings import get_string

# 🎆 Message Effects
EFFECT_ID = [
    5104841245755180586, 5107584321108051014, 5104841245755180586,
    5107584321108051014, 5104841245755180586, 5107584321108051014,
]

# 🌄 Random Start Images
Kanha = [
    "https://files.catbox.moe/v00l7e.jpg",
    "https://files.catbox.moe/uow54p.jpg",
    "https://files.catbox.moe/z0t6l3.jpg",
    "https://files.catbox.moe/jdw0il.jpg",
    "https://files.catbox.moe/izfi0y.jpg",
    "https://files.catbox.moe/7wx3ha.jpg",
    "https://files.catbox.moe/2u0srm.jpg",
    "https://files.catbox.moe/tqwy0q.jpg",
    "https://files.catbox.moe/vbgrx1.jpg"
]

REACTIONS = ["🍓", "🔥", "❤️", "⚡", "🎉", "🥰", "💫", "🎶", "🌟", "🕊️"]

# =====================================================
# START IN PRIVATE (Animations Removed)
# =====================================================
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # 🍓 Random reaction
    try:
        await message.react(random.choice(REACTIONS), big=True)
    except:
        pass

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            return await message.reply_photo(
                photo=random.choice(Kanha),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=help_panel(_),
            )

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return

        if name.startswith("inf"):
            m = await message.reply_text("🔎 Searching...")
            query = name.replace("info_", "", 1)
            results = VideosSearch(query, limit=1)
            res = await results.next()
            data = res["result"][0]
            thumbnail = data["thumbnails"][0]["url"].split("?")[0]
            
            key = InlineKeyboardMarkup([[InlineKeyboardButton(_["S_B_8"], url=data["link"]), InlineKeyboardButton(_["S_B_9"], url=config.SUPPORT_CHAT)]])
            await m.delete()
            return await message.reply_photo(photo=thumbnail, caption=_["start_6"].format(data["title"], data["duration"], data["viewCount"]["short"], data["publishedTime"], data["channel"]["link"], data["channel"]["name"], app.mention), reply_markup=key)

    # Direct Reply without any annoying animation
    out = private_panel(_)
    await message.reply_photo(
        photo=random.choice(Kanha),
        has_spoiler=True,
        message_effect_id=random.choice(EFFECT_ID),
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
    )

# =====================================================
# START IN GROUP
# =====================================================
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(start_panel(_)),
    )
    await add_served_chat(message.chat.id)

# =====================================================
# WELCOME HANDLER
# =====================================================
@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try: await message.chat.ban_member(member.id)
                except: pass

            if member.id == app.id:
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(_["start_5"].format(app.mention, f"t.me/{app.username}?start=sudolist", config.SUPPORT_CHAT))
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(message.from_user.first_name, app.mention, message.chat.title, app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
        except:
            pass
