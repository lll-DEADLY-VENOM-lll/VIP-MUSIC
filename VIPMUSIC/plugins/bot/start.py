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
    is_banned_user,
    is_on_off,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
from VIPMUSIC.utils.inline.start import alive_panel, private_panel, start_pannel

from .help import paginate_modules

# Global loop
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
async def auto_ban_handler(client, message):
    """Automatically ban blacklisted users from groups where the bot is admin"""
    if not message.from_user: return
    if await is_banned_user(message.from_user.id):
        try: 
            await message.chat.ban_member(message.from_user.id)
            await message.delete()
        except: pass

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    
    # Visual Reaction
    try: await message.react("⚡")
    except: pass
    
    # Deep Linking Logic
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        
        # Help Deep Link
        if name[0:4] == "help":
            keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
            return await message.reply_photo(
                photo=START_IMG_URL, 
                caption=_["help_1"], 
                reply_markup=keyboard
            )
        
        # Sudo List Deep Link
        if name[0:3] == "sud":
            from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
            return await sudoers_list(client=client, message=message, _=_)
            
        # Song Info Deep Link (Enhanced)
        if name[0:3] == "inf":
            m = await message.reply_text("🔍 Fetching Information...")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                ch_name = result["channel"]["name"]
            
            caption = (
                f"🎵 **Track Information**\n\n"
                f"📌 **Title:** {title[:30]}...\n"
                f"⏱️ **Duration:** {duration} Mins\n"
                f"👀 **Views:** {views}\n"
                f"👤 **Channel:** {ch_name}"
            )
            await m.delete()
            return await message.reply_photo(
                photo=thumbnail,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="✨ Play Now", callback_data=f"MusicStream {query}")]]),
            )

    # Standard Private Start
    out = private_panel(_)
    caption = _["start_2"].format(message.from_user.mention, app.mention)
    
    try:
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(out),
            message_effect_id="5104841245755180586" # Premium effect
        )
    except:
        await message.reply_photo(
            photo=config.START_IMG_URL, 
            caption=caption, 
            reply_markup=InlineKeyboardMarkup(out)
        )

    # Logging with more detail
    if await is_on_off(config.LOG):
        log_text = (
            f"👤 **New User Alert**\n\n"
            f"**Name:** {message.from_user.first_name}\n"
            f"**ID:** `{message.from_user.id}`\n"
            f"**User:** @{message.from_user.username}"
        )
        try: await app.send_message(get_log_id(), log_text)
        except: pass

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def group_start_handler(client, message: Message, _):
    uptime = get_readable_time(int(time.time() - _boot_))
    out = alive_panel(_)
    
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_7"].format(app.mention, uptime),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome_bot(client, message: Message):
    """Enhanced Welcome for the bot itself"""
    chat_id = message.chat.id
    await add_served_chat(chat_id)
    
    for member in message.new_chat_members:
        try:
            if member.id == app.id:
                language = await get_lang(chat_id)
                _ = get_string(language)
                userbot = await get_assistant(chat_id)
                
                welcome_text = (
                    f"✨ **Thanks for adding me to {message.chat.title}!**\n\n"
                    f"🔹 **Bot Status:** Online\n"
                    f"🔹 **Assistant:** @{userbot.username}\n"
                    f"🔹 **Language:** {language}\n\n"
                    f"Click the button below to see how to use me!"
                )
                
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=welcome_text,
                    reply_markup=InlineKeyboardMarkup(start_pannel(_))
                )
        except Exception as e:
            print(f"Welcome Error: {e}")

__MODULE__ = "Bot"
__HELP__ = """
✨ **Basic Commands** ✨

★ /start - Check if bot is alive.
★ /help - Get the help menu.
★ /stats - View bot performance.
★ /settings - Group settings.
"""
