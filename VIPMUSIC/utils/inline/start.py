from pyrogram.types import InlineKeyboardButton
import config
from VIPMUSIC import app # Updated from VIPMUSIC to KanhaMusic

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT, # Updated to SUPPORT_CHAT
            ),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text="ɪɴғᴏ 皿", callback_data="api_status"),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
            ),
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="settings_back_helper",
            ),
        ],
    ]
    return buttons

def alive_panel(_):
    # Isse bhi update kar diya naye variables ke saath
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"], 
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT
            ),
        ],
    ]
    return buttons

def music_start_panel(_):
    # Music panel ko bhi naye pattern me set kiya hai
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="ᴀʙᴏᴜᴛ 📝", callback_data="about"),
            InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ 🥀", callback_data="support"),
        ],
        [
            InlineKeyboardButton(text="۞ ғᴇᴀᴛᴜʀᴇ ۞", callback_data="feature")
        ],
    ]
    return buttons
