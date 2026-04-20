import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import InviteRequestSent, UserAlreadyParticipant, UserNotParticipant
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.database import get_assistant
from VIPMUSIC.utils.vip_ban import admin_filter

@app.on_message(
    filters.group
    & filters.command(["userbotjoin", f"userbotjoin@{app.username}"])
    & ~filters.private
)
async def join_group(client, message):
    chat_id = message.chat.id
    userbot = await get_assistant(chat_id)
    userbot_id = userbot.id
    done = await message.reply("**ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... ɪɴᴠɪᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ**")

    # Bot ki permissions check karein
    bot_member = await app.get_chat_member(chat_id, app.id)
    is_bot_admin = bot_member.status == ChatMemberStatus.ADMINISTRATOR

    # Check assistant status
    try:
        ubot_member = await app.get_chat_member(chat_id, userbot_id)
        if ubot_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
        
        if ubot_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
            if not is_bot_admin:
                return await done.edit_text("**❌ ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ. ᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴍᴀɴᴜᴀʟʟʏ ᴏʀ ɢɪᴠᴇ ᴍᴇ ʙᴀɴ ᴘᴏᴡᴇʀ.**")
            await app.unban_chat_member(chat_id, userbot_id)
            await asyncio.sleep(1)
    except UserNotParticipant:
        pass
    except Exception as e:
        return await done.edit_text(f"**Error:** `{e}`")

    # Joining Logic
    if message.chat.username: # Public Group
        try:
            await userbot.join_chat(message.chat.username)
            await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
        except UserAlreadyParticipant:
            await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ.**")
        except InviteRequestSent:
            try:
                await app.approve_chat_join_request(chat_id, userbot_id)
                await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.**")
            except:
                await done.edit_text("**📩 ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ sᴇɴᴛ. ᴘʟᴇᴀsᴇ ᴀᴘᴘʀᴏᴠᴇ ɪᴛ.**")
        except Exception:
            await done.edit_text("**❌ ᴀssɪsᴛᴀɴᴛ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴊᴏɪɴ. ᴍᴀᴋᴇ sᴜʀᴇ ɪ'ᴍ ᴀᴅᴍɪɴ.**")

    else: # Private Group
        if not is_bot_admin:
            return await done.edit_text("**❌ ɪ ɴᴇᴇᴅ 'ɪɴᴠɪᴛᴇ ᴜsᴇʀs' ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ ᴛᴏ ɪɴᴠɪᴛᴇ ᴍʏ ᴀssɪsᴛᴀɴᴛ.**")
        
        try:
            invite_link = await app.create_chat_invite_link(chat_id)
            await userbot.join_chat(invite_link.invite_link)
            await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
        except UserAlreadyParticipant:
            await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ.**")
        except InviteRequestSent:
            try:
                await app.approve_chat_join_request(chat_id, userbot_id)
                await done.edit_text("**✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.**")
            except:
                await done.edit_text("**📩 ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ sᴇɴᴛ. ᴘʟᴇᴀsᴇ ᴀᴘᴘʀᴏᴠᴇ ɪᴛ.**")
        except Exception as e:
            await done.edit_text(f"**❌ ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ ᴀssɪsᴛᴀɴᴛ.**\n**Error:** `{e}`")

@app.on_message(filters.command("userbotleave") & filters.group & admin_filter)
async def leave_one(client, message):
    try:
        userbot = await get_assistant(message.chat.id)
        await userbot.leave_chat(message.chat.id)
        await message.reply("**✅ ᴀssɪsᴛᴀɴᴛ ʟᴇғᴛ ᴛʜɪs ᴄʜᴀᴛ.**")
    except Exception as e:
        await message.reply(f"**Error:** `{e}`")

@app.on_message(filters.command(["leaveall"]) & SUDOERS)
async def leave_all(client, message):
    status_msg = await message.reply("🔄 **ᴀssɪsᴛᴀɴᴛ ʟᴇᴀᴠɪɴɢ ᴀʟʟ ᴄʜᴀᴛs...**")
    left = 0
    failed = 0
    userbot = await get_assistant(message.chat.id)
    
    async for dialog in userbot.get_dialogs():
        try:
            await userbot.leave_chat(dialog.chat.id)
            left += 1
            if left % 5 == 0: # Status update every 5 chats
                await status_msg.edit(f"**ʟᴇᴀᴠɪɴɢ...**\n\n✅ **ʟᴇғᴛ:** `{left}`\n❌ **ғᴀɪʟᴇᴅ:** `{failed}`")
        except Exception:
            failed += 1
        await asyncio.sleep(1) # Flood wait avoid karne ke liye
    
    await status_msg.edit(f"**✅ ᴘʀᴏᴄᴇss ᴄᴏᴍᴘʟᴇᴛᴇᴅ!**\n\n**ʟᴇғᴛ:** `{left}` ᴄʜᴀᴛs\n**ғᴀɪʟᴇᴅ:** `{failed}` ᴄʜᴀᴛs")

__MODULES__ = "Userbotjoin"
__HELP__ = """
/userbotjoin - Assistant ko group mein bulaye.
/userbotleave - Assistant ko group se bhagaye.
/leaveall - Assistant ko saare groups se nikaale (Sudoers only).
"""
