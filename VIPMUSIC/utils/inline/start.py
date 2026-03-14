from pyrogram.types import InlineKeyboardButton
import config
from config import SUPPORT_GROUP, SUPPORT_CHANNEL
from VIPMUSIC import app

# --- PREMIUM LUXURY LAYOUT ---

def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="✧ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✧",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🛠️ ʜᴇʟᴘ", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="✨ sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="📢 ᴜᴘᴅᴀᴛᴇs", url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="💎 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 💎",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="𓊈 sᴜᴘᴘᴏʀᴛ 𓊉", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="𓊈 ᴜᴘᴅᴀᴛᴇs 𓊉", url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(text="۞ ꜰᴇᴀᴛᴜʀᴇs ۞", callback_data="settings_back_helper")
        ],
        [
            InlineKeyboardButton(text="👑 ᴏᴡɴᴇʀ", url=f"https://t.me/Your_Owner_Username"),
            InlineKeyboardButton(text="🚀 sᴏᴜʀᴄᴇ", callback_data="feature"),
        ],
    ]
    return buttons


def alive_panel(_):
    # Ek line mein do premium looking buttons
    buttons = [
        [
            InlineKeyboardButton(
                text="✫ ᴀᴅᴅ ᴍᴇ ✫", url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text="🎧 sᴜᴘᴘᴏʀᴛ", url=f"{SUPPORT_GROUP}"),
        ],
    ]
    return buttons


def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="💠 ᴀᴅᴅ ᴍᴇ ɪɴ ɴᴇᴡ ɢʀᴏᴜᴘ 💠",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="📑 ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton(text="🛡️ sᴜᴘᴘᴏʀᴛ", callback_data="support"),
        ],
        [
            InlineKeyboardButton(text="⭐ ꜰᴇᴀᴛᴜʀᴇ", callback_data="feature"),
            InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_helper"),
        ],
    ]
    return buttons
