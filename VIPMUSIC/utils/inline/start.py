from pyrogram.types import InlineKeyboardButton
import config
from VIPMUSIC import app

def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="⚜️ ʟᴀɴɢᴜᴀɢᴇ", callback_data="LG"),
            InlineKeyboardButton(text="🛡️ ᴘᴏʟɪᴄʏ", url=config.UPSTREAM_REPO),
        ],
        [
            InlineKeyboardButton(text="📡 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="📨 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(
                text="🔍 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ? ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ", callback_data="settings_back_helper"
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="⚜️ ʟᴀɴɢᴜᴀɢᴇ", callback_data="LG"),
            InlineKeyboardButton(text="🛡️ ᴘᴏʟɪᴄʏ", url=config.UPSTREAM_REPO),
        ],
        [
            InlineKeyboardButton(text="📡 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="📨 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(
                text="🔍 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ? ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ", callback_data="settings_back_helper"
            ),
        ],
    ]
    return buttons


def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(text="⚜️ ʟᴀɴɢᴜᴀɢᴇ", callback_data="LG"),
            InlineKeyboardButton(text="🛡️ ᴘᴏʟɪᴄʏ", url=config.UPSTREAM_REPO),
        ],
        [
            InlineKeyboardButton(text="📨 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ➕",
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
        ],
    ]
    return buttons
