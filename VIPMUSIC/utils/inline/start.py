# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, <https://github.com/THE-VIP-BOY-OP>.
# This file is part of <https://github.com/THE-VIP-BOY-OP/VIP-MUSIC> project,
# and is released under the "GNU v3.0 License Agreement".
# Please see <https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE>
# All rights reserved.

from pyrogram.types import InlineKeyboardButton
import config
from VIPMUSIC import app

# 1. Main Start Panel (जब बोट ग्रुप में स्टार्ट हो)
def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="💠 𝐀𝙳𝙳 𝙼𝙴 𝙸𝙽 𝙽𝙴𝚆 𝙶𝚁𝙾𝚄𝙿𝚂 💠",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="۞ 𝐇𝙴𝙻𝙿 ۞", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="☢ 𝐒𝙴𝚃 ☢", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="✡ 𝐆𝚁𝙾𝚄𝙿 ✡", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="🥀 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 🥀", url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons

# 2. Private Panel (जब बोट PM में स्टार्ट हो)
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="💠 𝐀𝙳𝙳 𝙼𝙴 𝙸𝙽 𝙽𝙴𝚆 𝙶𝚁𝙾𝚄𝙿𝚂 💠",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="𝐆𝚁𝙾𝚄𝙿✨", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="𝐌ᴏʀᴇ🥀", url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(
                text="۞ 𝐅𝙴𝙰𝚃𝚄𝚁𝙴𝚂 ۞", callback_data="settings_back_helper"
            )
        ],
    ]
    return buttons

# 3. Music Start Panel (यही फंक्शन गायब था - Error Fix)
def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="۞ 𝐇𝙴𝙻𝙿 ۞", callback_data="settings_back_helper"
            ),
            InlineKeyboardButton(
                text="☢ 𝐒𝙴𝚃 ☢", callback_data="settings_helper"
            ),
        ],
        [
            InlineKeyboardButton(text="✡ 𝐆𝚁𝙾𝚄𝙿 ✡", url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons

# 4. Alive Panel
def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="✿︎ ᴀᴅᴅ ᴍᴇ ✿︎", url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons
