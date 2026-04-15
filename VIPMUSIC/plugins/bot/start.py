#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import time
import random
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from strings import get_string
from VIPMUSIC import HELPABLE, YouTube, app
from VIPMUSIC.misc import SUDOERS, _boot_
from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
from VIPMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_assistant,
    get_lang,
    get_userss,
    is_banned_user,
    is_on_off,
    is_served_private_chat,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
from VIPMUSIC.utils.functions import MARKDOWN, WELCOMEHELP
from VIPMUSIC.utils.inline import alive_panel, private_panel, start_panel

from .help import paginate_modules

# ---------------- CUSTOM DATA ---------------- #

EFFECT_ID = [
    5104841245755180586, 5107584321108051014, 5104841245755180586,
    5107584321108051014, 5104841245755180586, 5107584321108051014,
    5104841245755180586, 5107584321108051014,
]

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

REACTIONS = ["🍓", "🔥", "❤️", "⚡", "🎉", "🥰", "👏", "💫", "🎶", "🌟", "💩", "👍", "👎"]

# ---------------------------------------------- #

loop = asyncio.get_running_loop()

def get_log_id():
    log_id = config.LOG_GROUP_ID
    if not log_id:
        return None
    try:
        log_id = str(log_id).strip()
        if not log_id.startswith("-100"):
            if log_id.startswith("-"):
                return int(log_id)
            else:
                return int(f"-100{log_id}")
        return int(log_id)
    except Exception:
        return None

@app.on_message(group=-1)
async def ban_new(client, message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    if await is_banned_user(user_id):
        try:
            await message.chat.ban_member(user_id)
            await message.reply_text("❌ You are banned from using this bot!")
        except:
            pass

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    
    try:
        await message.react(random.choice(REACTIONS))
    except:
        pass
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        
        if name[0:4] == "help":
            keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
            return await message.reply_photo(photo=random.choice(Kanha), caption=_["help_1"], reply_markup=keyboard)

        if name[0:4] == "song":
            return await message.reply_text(_["song_2"])

        if name == "mkdwn_help":
            return await message.reply(MARKDOWN, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        if name == "greetings":
            return await message.reply(WELCOMEHELP, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        if name[0:3] == "sta":
            m = await message.reply_text("🔎 Fetching your personal stats...")
            stats = await get_userss(message.from_user.id)
            if not stats:
                return await m.edit(_["ustats_1"])

            def get_stats():
                results = {str(i): stats[i]["spot"] for i in stats}
                list_arranged = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
                tota = sum(results.values())
                msg = ""
                limit = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    if limit == 10: break
                    if limit == 0: videoid = vidid
                    limit += 1
                    title = (stats.get(vidid)["title"][:35]).title()
                    if vidid == "telegram":
                        msg += f"🔗 **Telegram Files**: {count} times\n"
                    else:
                        msg += f"🔗 [{title}](https://www.youtube.com/watch?v={vidid}) **{count}**\n"
                return videoid, _["ustats_2"].format(len(stats), tota, limit) + "\n" + msg

            try:
                videoid, stat_msg = await loop.run_in_executor(None, get_stats)
                thumbnail = await YouTube.thumbnail(videoid, True)
                await m.delete()
                await message.reply_photo(photo=thumbnail, caption=stat_msg)
            except:
                await m.edit("Failed to fetch statistics.")
            return

        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            return

    out = private_panel(_)
    try:
        await message.reply_photo(
            photo=random.choice(Kanha),
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
            message_effect_id=random.choice(EFFECT_ID)
        )
    except Exception:
        await message.reply_photo(
            photo=random.choice(Kanha), 
            caption=_["start_2"].format(message.from_user.mention, app.mention), 
            reply_markup=InlineKeyboardMarkup(out)
        )

    if await is_on_off(config.LOG):
        log_id = get_log_id()
        if log_id:
            try:
                await app.send_message(log_id, f"👤 {message.from_user.mention} started the bot.")
            except:
                pass

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    out = alive_panel(_)
    uptime = get_readable_time(int(time.time() - _boot_))
    await message.reply_photo(
        photo=random.choice(Kanha),
        caption=_["start_7"].format(app.mention, uptime),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True) and not await is_served_private_chat(chat_id):
        return await app.leave_chat(chat_id)
    
    await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_5"])
                    return await app.leave_chat(chat_id)
                if chat_id in await blacklisted_chats():
                    await message.reply_text(_["start_6"].format(f"https://t.me/{app.username}?start=sudolist"))
                    return await app.leave_chat(chat_id)
                
                userbot = await get_assistant(chat_id)
                await message.reply_text(_["start_2"].format(app.mention, userbot.username, userbot.id), reply_markup=InlineKeyboardMarkup(start_panel(_)))
            
            if member.id in config.OWNER_ID:
                await message.reply_text(_["start_3"].format(app.mention, member.mention))
            elif member.id in SUDOERS:
                await message.reply_text(_["start_4"].format(app.mention, member.mention))
        except:
            pass

__MODULE__ = "Bot"
__HELP__ = """
<b>★ /stats</b> - Get Top 10 Stats
<b>★ /sudolist</b> - Check Sudo Users
<b>★ /lyrics</b> - Search Lyrics
<b>★ /song</b> - Download Songs
<b>★ /player</b> - Music Control Panel
<b>★ /queue</b> - Show Music Queue
"""
