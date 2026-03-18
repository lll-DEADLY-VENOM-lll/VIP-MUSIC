import asyncio
import os
import time
import wget
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from yt_dlp import YoutubeDL

from VIPMUSIC import app
from VIPMUSIC.platforms.Youtube import YouTubeAPI

# Initialize YouTube API
YouTube = YouTubeAPI()

# User trackers
user_last_CallbackQuery_time = {}
BANNED_USERS = []
SPAM_WINDOW_SECONDS = 30

@app.on_callback_query(filters.regex("downloadvideo") & ~filters.user(BANNED_USERS))
async def download_video(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Spam Check
    if current_time - user_last_CallbackQuery_time.get(user_id, 0) < SPAM_WINDOW_SECONDS:
        return await CallbackQuery.answer("⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ 30 ɪɴ sᴇᴄᴏɴᴅs!", show_alert=True)
    
    videoid = CallbackQuery.data.split(None, 1)[1]
    mention = CallbackQuery.from_user.mention

    # --- STEP 1: DM CHECK ---
    try:
        check = await client.send_message(user_id, "✨ **ᴄʜᴇᴄᴋɪɴɢ ᴅᴍ ᴄᴏɴɴᴇᴄᴛɪᴏɴ...**")
        await check.delete()
    except (UserIsBlocked, PeerIdInvalid):
        return await CallbackQuery.message.reply_text(
            f"❌ **ʜᴇʏ {mention}, ᴀᴀᴘᴋᴀ ᴅᴍ ʙᴀɴᴅ ʜᴀɪ!**\n\nᴘᴇʜʟᴇ ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ʙᴜᴛᴛᴏɴ ᴘᴇ ᴄʟɪᴄᴋ ᴋᴀʀᴋᴇ ᴍᴜᴊʜᴇ **sᴛᴀʀᴛ** ᴋᴀʀᴏ, ᴘʜɪʀ ᴅᴏᴡɴʟᴏᴀᴅ ʜᴏɢᴀ.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🚀 sᴛᴀʀᴛ ɪɴ ᴘᴍ", url=f"https://t.me/{app.username}?start=help")
            ]])
        )

    user_last_CallbackQuery_time[user_id] = current_time

    # --- STEP 2: GET DETAILS & SHOW LOADING IMAGE ---
    details = await YouTube.details(videoid, videoid=True)
    if not details:
        return await CallbackQuery.message.reply_text("❌ **ᴠɪᴅᴇᴏ ɴᴏᴛ ғᴏᴜɴᴅ!**")

    title, duration_min, duration_sec, thumbnail, vidid = details
    url = f"https://www.youtube.com/watch?v={vidid}"

    # Group mein loading image (thumbnail) bhejna
    pablo = await client.send_photo(
        CallbackQuery.message.chat.id,
        photo=thumbnail,
        caption=f"**✨ ɪᴍᴀɢɪɴɪɴɢ ʏᴏᴜʀ ᴠɪᴅᴇᴏ...**\n\n**📝 ᴛɪᴛʟᴇ:** `{title[:50]}...`"
    )

    # --- STEP 3: DOWNLOAD VIDEO ---
    await pablo.edit_caption(f"**📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ...**\n\n**⏳ ᴅᴜʀᴀᴛɪᴏɴ:** `{duration_min}`")

    if not os.path.exists("downloads"): os.makedirs("downloads")
    file_path = f"downloads/{vidid}.mp4"
    
    opts = {
        "format": "best",
        "outtmpl": file_path,
        "quiet": True,
    }

    try:
        with YoutubeDL(opts) as ytdl:
            await asyncio.to_thread(ytdl.extract_info, url, download=True)
    except Exception as e:
        return await pablo.edit_caption(f"**❌ ᴅᴏᴡɴʟᴏᴀᴅ ᴇʀʀᴏʀ:** `{e}`")

    # --- STEP 4: UPLOAD VIDEO ---
    await pablo.edit_caption(f"**📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ʏᴏᴜʀ ᴘᴍ...**\n\n**👤 ᴜsᴇʀ:** {mention}")

    try:
        await client.send_video(
            user_id,
            video=file_path,
            duration=duration_sec,
            caption=f"❄ **ᴛɪᴛʟᴇ :** [{title}]({url})\n\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {mention}",
            thumb=None, # Thumbnail automatically handled by telegram usually
            supports_streaming=True,
        )
        await pablo.edit_caption(f"**✅ ᴠɪᴅᴇᴏ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ɪɴ ᴘᴍ!**")
        await asyncio.sleep(5)
        await pablo.delete()
    except Exception:
        await pablo.edit_caption(f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ! ᴅᴍ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ.**")
    finally:
        if os.path.exists(file_path): os.remove(file_path)


@app.on_callback_query(filters.regex("downloadaudio") & ~filters.user(BANNED_USERS))
async def download_audio(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    if current_time - user_last_CallbackQuery_time.get(user_id, 0) < SPAM_WINDOW_SECONDS:
        return await CallbackQuery.answer("⏳ Wait 30s!", show_alert=True)

    videoid = CallbackQuery.data.split(None, 1)[1]
    mention = CallbackQuery.from_user.mention

    # --- DM CHECK ---
    try:
        check = await client.send_message(user_id, "✨ **ᴄʜᴇᴄᴋɪɴɢ ᴄᴏɴɴᴇᴄᴛɪᴏɴ...**")
        await check.delete()
    except (UserIsBlocked, PeerIdInvalid):
        return await CallbackQuery.message.reply_text(
            f"❌ **ʜᴇʏ {mention}, ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴍᴇ ɪɴ ᴘᴍ.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 sᴛᴀʀᴛ", url=f"https://t.me/{app.username}?start=help")]])
        )

    user_last_CallbackQuery_time[user_id] = current_time

    details = await YouTube.details(videoid, videoid=True)
    if not details: return

    title, duration_min, duration_sec, thumbnail, vidid = details
    url = f"https://www.youtube.com/watch?v={vidid}"

    # Loading Image for Audio
    pablo = await client.send_photo(
        CallbackQuery.message.chat.id,
        photo=thumbnail,
        caption=f"**🎵 ɪᴍᴀɢɪɴɪɴɢ ʏᴏᴜʀ ᴀᴜᴅɪᴏ...**"
    )

    await pablo.edit_caption(f"**📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ...**\n\n**📝 ᴛɪᴛʟᴇ:** `{title[:50]}...`")

    file_path = f"downloads/{vidid}.mp3"
    opts = {
        "format": "bestaudio/best",
        "outtmpl": file_path,
        "quiet": True,
    }

    try:
        with YoutubeDL(opts) as ytdl:
            await asyncio.to_thread(ytdl.extract_info, url, download=True)
    except Exception as e:
        return await pablo.edit_caption(f"**❌ ᴇʀʀᴏʀ:** `{e}`")

    await pablo.edit_caption(f"**📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ...**")

    try:
        await client.send_audio(
            user_id,
            audio=file_path,
            title=title,
            duration=duration_sec,
            caption=f"❄ **ᴛɪᴛʟᴇ :** [{title}]({url})\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {mention}",
        )
        await pablo.edit_caption(f"**✅ ᴀᴜᴅɪᴏ sᴇɴᴛ ɪɴ ᴘᴍ!**")
        await asyncio.sleep(5)
        await pablo.delete()
    except Exception:
        await pablo.edit_caption(f"**❌ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ.**")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
