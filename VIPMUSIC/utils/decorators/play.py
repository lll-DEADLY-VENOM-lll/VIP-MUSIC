import asyncio
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PLAYLIST_IMG_URL, PRIVATE_BOT_MODE
from config import SUPPORT_GROUP as SUPPORT_CHAT
from strings import get_string
from VIPMUSIC import YouTube, app
from VIPMUSIC.core.call import VIP
from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_commanddelete_on,
    is_maintenance,
    is_served_private_chat,
    set_loop,
)
from VIPMUSIC.utils.inline import botplaylist_markup

# Adminlist ko import karein ya access karein (agar aapke global vars mein hai)
from VIPMUSIC.utils.database import get_authuser_names # Example agar list database se hai

links = {}

def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        
        # 1. Anonymous Admin Check
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(_["general_4"], reply_markup=upl)

        # 2. Maintenance Check
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )

        # 3. Private Bot Mode Check
        if PRIVATE_BOT_MODE == str(True):
            if not await is_served_private_chat(message.chat.id):
                await message.reply_text(
                    "**ᴘʀɪᴠᴀᴛᴇ ᴍᴜsɪᴄ ʙᴏᴛ**\n\nᴏɴʟʏ ғᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴄʜᴀᴛs. ᴀsᴋ ᴍʏ ᴏᴡɴᴇʀ ᴛᴏ ᴀʟʟᴏᴡ ʏᴏᴜʀ ᴄʜᴀᴛ ғɪʀsᴛ."
                )
                return await app.leave_chat(message.chat.id)

        # 4. Command Delete Check
        if await is_commanddelete_on(message.chat.id):
            try:
                await message.delete()
            except:
                pass

        # 5. Media & URL Extraction
        audio_telegram = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
        video_telegram = (message.reply_to_message.video or message.reply_to_message.document) if message.reply_to_message else None
        url = await YouTube.url(message)

        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["playlist_1"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # 6. Channel Play Mode Check
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_12"])
            try:
                chat = await app.get_chat(chat_id)
                channel = chat.title
            except:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id
            channel = None

        # 7. Active Video Chat Check
        try:
            is_call_active = (await app.get_chat(chat_id)).is_call_active
            if not is_call_active:
                return await message.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ғᴏᴜɴᴅ. ᴩʟᴇᴀsᴇ sᴛᴀʀᴛ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ.")
        except:
            pass

        # 8. Playback Permissions
        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                # Assuming adminlist logic is handled globally or via database
                # if message.from_user.id not in admins: return ...
                pass

        # Video/ForcePlay Flags
        video = True if (message.command[0][0] == "v" or "-v" in message.text) else None
        fplay = True if message.command[0][-1] == "e" else None

        if fplay and not await is_active_chat(chat_id):
            return await message.reply_text(_["play_18"])

        # 9. Assistant & Joining Logic (Updated)
        userbot = await get_assistant(chat_id)
        userbot_id = userbot.id
        
        try:
            get_member = await app.get_chat_member(chat_id, userbot_id)
            if get_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                try:
                    await app.unban_chat_member(chat_id, userbot_id)
                except:
                    return await message.reply_text(_["call_2"].format(userbot.username, userbot_id))
        except UserNotParticipant:
            # Join via Username if Public
            chat_obj = await app.get_chat(chat_id)
            if chat_obj.username:
                try:
                    await userbot.join_chat(chat_obj.username)
                except Exception as e:
                    return await message.reply_text(_["call_3"].format(app.mention, type(e).__name__))
            else:
                # Join via Invite Link if Private
                try:
                    invitelink = await client.export_chat_invite_link(chat_id)
                except ChatAdminRequired:
                    return await message.reply_text(_["call_1"])
                except Exception as e:
                    return await message.reply_text(_["call_3"].format(app.mention, type(e).__name__))

                m_wait = await message.reply_text(_["call_5"])
                try:
                    await userbot.join_chat(invitelink)
                    await m_wait.edit(_["call_6"].format(app.mention))
                    await asyncio.sleep(2)
                    await m_wait.delete()
                except InviteRequestSent:
                    await app.approve_chat_join_request(chat_id, userbot_id)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await m_wait.edit(_["call_3"].format(type(e).__name__))

        # 10. Voice Chat Stream Logic
        try:
            # Sync userbot with VC
            await userbot.resolve_peer(chat_id)
            participants = [member.chat.id async for member in userbot.get_call_members(chat_id)]
            if await is_active_chat(chat_id) and userbot_id not in participants:
                await VIP.st_stream(chat_id)
                await set_loop(chat_id, 0)
        except Exception:
            pass

        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper
