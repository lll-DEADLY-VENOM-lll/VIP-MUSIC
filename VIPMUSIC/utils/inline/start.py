from pyrogram.types import InlineKeyboardButton
import config
from config import SUPPORT_GROUP, SUPPORT_CHANNEL
from VIPMUSIC import app

# --- UNIQUE START PANEL (Aesthetic Style) ---
def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="〆 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ 〆",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="⛩️ ʜᴇʟᴘ", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="🎐 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="📜 ᴜᴘᴅᴀᴛᴇs", url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons


# --- UNIQUE PRIVATE PANEL (Premium VIP Look) ---
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="✨ ɪɴᴠɪᴛᴇ ᴍᴇ ɴᴏᴡ ✨",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="💠 ɢʀᴏᴜᴘ", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="🪐 ᴜᴘᴅᴀᴛᴇs", url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(
                text="📜 ᴇxᴘʟᴏʀᴇ ғᴇᴀᴛᴜʀᴇs 📜", callback_data="settings_back_helper"
            )
        ],
        [
            InlineKeyboardButton(text="🍷 ᴏᴡɴᴇʀ", url=f"https://t.me/Your_Owner_ID"),
            InlineKeyboardButton(text="🎋 sᴏᴜʀᴄᴇ", url=f"https://github.com/Your_Repo"),
        ],
        [
            InlineKeyboardButton(text="👑 ᴠɪᴘ ɴᴇᴛᴡᴏʀᴋ 👑", url=f"https://t.me/Your_Main_Channel"),
        ],
    ]
    return buttons


# --- UNIQUE MUSIC START PANEL ---
def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(text="🚀 ɢᴇᴛ ʜᴇʟᴘ 🚀", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="🛠 ᴛᴏᴏʟs", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="✨ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ✨", url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons


# --- UNIQUE ALIVE PANEL (Minimalist & Clean) ---
def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="❅ ᴀᴅᴅ ᴍᴇ ❅", url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text="❅ sᴜᴘᴘᴏʀᴛ ❅", url=f"{SUPPORT_GROUP}"),
        ],
        [
            InlineKeyboardButton(text="ッ ᴏᴡɴᴇʀ ッ", url=f"https://t.me/Your_Owner_ID"),
        ]
    ]
    return buttons
