from pyrogram.types import InlineKeyboardButton

import config
from VIPMUSIC import app

# Yahan humne 'start_panel' ko 'private_panel' mein badal diya hai taki error fix ho jaye
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text="⚜️ ʟᴀɴɢᴜᴀɢᴇ",
                callback_data="language"
            ),
            InlineKeyboardButton(
                text="🛡 ᴘᴏʟɪᴄʏ",
                callback_data="policy"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✉️ ᴄʜᴀɴɴᴇʟ",
                url=config.SUPPORT_CHANNEL
            ),
            InlineKeyboardButton(
                text="✉️ sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_GROUP
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔎 ʜᴏᴡ ᴛᴏ ᴜsᴇ? ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ",
                callback_data="help_menu"
            )
        ],
    ]
    return buttons

# Ye extra function hai taaki agar kahin 'start_panel' use ho raha ho toh error na aaye
def start_panel(_):
    return private_panel(_)
