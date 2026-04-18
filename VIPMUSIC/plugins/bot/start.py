import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_string
from VIPMUSIC import HELPABLE, Telegram, YouTube, app
from VIPMUSIC.misc import SUDOERS, _boot_
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

# THE FIX: Import specifically from the .start file inside inline folder
from VIPMUSIC.utils.inline.start import alive_panel, private_panel, start_pannel

from .help import paginate_modules

loop = asyncio.get_running_loop()

def get_log_id():
    log_id = config.LOG_GROUP_ID
    if not log_id: return None
    try:
        log_id = str(log_id).strip()
        if not log_id.startswith("-100"):
            return int(log_id) if log_id.startswith("-") else int(f"-100{log_id}")
        return int(log_id)
    except: return log_id

@app.on_message(group=-1)
async def ban_new(client, message):
    if not message.from_user: return
    if await is_banned_user(message.from_user.id):
        try: await message.chat.ban_member(message.from_user.id)
        except: pass

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    try: await message.react("🕊️")
    except: pass
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
            return await message.reply_photo(photo=START_IMG_URL, caption=_["help_1"], reply_markup=keyboard)
        if name[0:3] == "sud":
            from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
            return await sudoers_list(client=client, message=message, _=_)

    out = private_panel(_)
    try:
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
            message_effect_id="5311823902341673323"
        )
    except:
        await message.reply_photo(photo=config.START_IMG_URL, caption=_["start_2"].format(message.from_user.mention, app.mention), reply_markup=InlineKeyboardMarkup(out))

    if await is_on_off(config.LOG):
        try: await app.send_message(get_log_id(), f"**#NewUser**\n\n{message.from_user.mention} started the bot.")
        except: pass

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    out = alive_panel(_)
    uptime = get_readable_time(int(time.time() - _boot_))
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_7"].format(app.mention, uptime),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)
            if member.id == app.id:
                userbot = await get_assistant(chat_id)
                await message.reply_text(_["start_2"].format(app.mention, userbot.username, userbot.id), reply_markup=InlineKeyboardMarkup(start_pannel(_)))
        except: pass

__MODULE__ = "Bot"
__HELP__ = "★ /start - Start the bot\n★ /stats - Get bot stats"
