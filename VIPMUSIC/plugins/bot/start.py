import random
import time
import asyncio

from py_yt import VideosSearch
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
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
from VIPMUSIC.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, LOGGER_ID, START_IMG_URL
from strings import get_string

# 🎆 Message Effects (Premium Effects)
EFFECT_ID = [
    "5311823902341673323", # Heart
    "5104841245755180586", # Star
    "5107584321108051014", # Fire
    "5046509860489231901", # Party
]

# 🌄 Random Start Images (Kanha)
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

# 🍓 Random Reactions
REACTIONS = ["🍓", "🔥", "❤️", "⚡", "🎉", "🥰", "👏", "💫", "🎶", "🌟", "👍"]

# =====================================================
# PRIVATE START HANDLER
# =====================================================
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # 1. Random Reaction
    try:
        await message.react(random.choice(REACTIONS), big=True)
    except:
        pass

    # 2. Deep Link Handling (help, song, sudo, info)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # Help Link
        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=random.choice(Kanha),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        # Sudo List Link
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return

        # Track/Video Info Link
        if name.startswith("inf"):
            m = await message.reply_text("🔎 Searching...")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"

            try:
                results = VideosSearch(query, limit=1)
                res = await results.next()
                data = res["result"][0]

                title = data["title"]
                duration = data["duration"]
                views = data["viewCount"]["short"]
                thumbnail = data["thumbnails"][0]["url"].split("?")[0]
                channellink = data["channel"]["link"]
                channel = data["channel"]["name"]
                link = data["link"]
                published = data["publishedTime"]

                searched_text = _["start_6"].format(
                    title, duration, views, published, channellink, channel, app.mention
                )

                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(_["S_B_8"], url=link),
                            InlineKeyboardButton(_["S_B_9"], url=config.SUPPORT_CHAT),
                        ],
                        [InlineKeyboardButton("🗑 Close", callback_data="close")]
                    ]
                )

                await m.delete()
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    has_spoiler=True,
                    caption=searched_text,
                    reply_markup=key,
                )
            except Exception as e:
                await m.edit(f"Error fetching info: {e}")
            return

    # 3. Main Start Message
    out = private_panel(_)
    await message.reply_photo(
        photo=random.choice(Kanha),
        has_spoiler=True,
        message_effect_id=random.choice(EFFECT_ID),
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
    )

    # Logger (If enabled)
    if await is_on_off(2): # Assuming 2 is the toggle for Logger
        try:
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"👤 {message.from_user.mention} has started the bot.\n🆔 `<code>{message.from_user.id}</code>`"
            )
        except:
            pass


# =====================================================
# GROUP START HANDLER
# =====================================================
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        photo=config.START_IMG_URL,
        has_spoiler=True,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)


# =====================================================
# WELCOME & BOT ADDED HANDLER
# =====================================================
@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            # 1. Ban Check
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            # 2. Bot Joined
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text("Supergroup is required for this bot.")
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text("This group is blacklisted!")
                    return await app.leave_chat(message.chat.id)

                language = await get_lang(message.chat.id)
                _ = get_string(language)
                out = start_panel(_)

                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name if message.from_user else "User",
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)

        except Exception as e:
            print(f"Error in Welcome: {e}")

__MODULE__ = "Bot"
__HELP__ = "★ /start - Start the bot\n★ /help - Get help menu"
