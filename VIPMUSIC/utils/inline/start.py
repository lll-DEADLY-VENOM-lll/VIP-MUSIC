from pyrogram.types import InlineKeyboardButton
import config
from config import SUPPORT_GROUP, SUPPORT_CHANNEL
from VIPMUSIC import app

# --- Start Panel (Group ke liye) ---
def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🛠 ʜᴇʟᴘ", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="👥 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons

# --- Private Panel (Bot DM ke liye) ---
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ɪɴ ɴᴇᴡ ɢʀᴏᴜᴘs ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="📢 ᴜᴘᴅᴀᴛᴇs", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
        ],
        [
            InlineKeyboardButton(text="🕹 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs", callback_data="settings_back_helper")
        ],
        [
            InlineKeyboardButton(text="❄️ ᴅᴇᴠᴇʟᴏᴘᴇʀ ❄️", url=f"https://t.me/Your_Username_Here"), # Apna username daal sakte hain
        ],
    ]
    return buttons

# --- Alive Panel (Alive command ke liye) ---
def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="🚀 ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text="🌐 sᴜᴘᴘᴏʀᴛ", url=f"{SUPPORT_GROUP}"),
        ],
    ]
    return buttons

# --- Music Start Panel (Music specific) ---
def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="🎵 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ 🎵",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="📖 ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton(text="🌟 ғᴇᴀᴛᴜʀᴇs", callback_data="feature"),
        ],
        [
            InlineKeyboardButton(text="🛡 sᴜᴘᴘᴏʀᴛ", callback_data="support"),
            InlineKeyboardButton(text="🥀 ᴏᴡɴᴇʀ", url=f"https://t.me/Your_Username_Here"),
        ],
    ]
    return buttons
