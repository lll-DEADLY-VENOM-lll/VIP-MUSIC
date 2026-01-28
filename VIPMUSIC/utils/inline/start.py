# ---------------------------------------------------------------------------------
#                                 👑 VIP MUSIC 👑
# ---------------------------------------------------------------------------------
# Copyright (C) 2025 VIP MUSIC Team
# Developer: Nand Yaduwanshi (NoxxOP)
#
# All rights reserved. 
# This code is an intellectual property of VIP MUSIC.
# Unauthorized copying, redistribution, or modification is strictly prohibited.
#
# Professional English Version - Premium Box Layout
# ---------------------------------------------------------------------------------

from pyrogram.types import InlineKeyboardButton
import config
from config import SUPPORT_GROUP, SUPPORT_CHANNEL, OWNER_ID
from VIPMUSIC import app

# ==========================================
# 1. PRIVATE PANEL (Premium Box Layout)
# ==========================================
def private_panel(_):
    buttons = [
        [
            # Full Width Box
            InlineKeyboardButton(
                text="✨ INVITE ME NOW ✨",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            # Paired Boxes (Side-by-Side)
            InlineKeyboardButton(text="💠 GROUP", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="🪐 UPDATES", url=config.SUPPORT_CHANNEL),
        ],
        [
            # Full Width Box
            InlineKeyboardButton(
                text="📜 EXPLORE FEATURES 📜", callback_data="settings_back_helper"
            )
        ],
        [
            # Paired Boxes (Side-by-Side)
            InlineKeyboardButton(text="🍷 OWNER", url=f"tg://openmessage?user_id={config.OWNER_ID}"),
            InlineKeyboardButton(text="🎋 SOURCE", url=f"https://github.com/VIP-MUSIC/VIP-MUSIC"),
        ],
        [
            # Full Width Box
            InlineKeyboardButton(text="👑 VIP NETWORK 👑", url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons


# ==========================================
# 2. START PANEL (Group Start Layout)
# ==========================================
def start_pannel(_):
    buttons = [
        [
            # Full Width
            InlineKeyboardButton(
                text="〆 ADD ME TO YOUR CHAT 〆",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            # Paired Boxes
            InlineKeyboardButton(text="⛩️ HELP", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="⚙️ SETTINGS", callback_data="settings_helper"),
        ],
        [
            # Paired Boxes
            InlineKeyboardButton(text="🎐 SUPPORT", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="📜 UPDATES", url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons


# ==========================================
# 3. ALIVE PANEL (Clean Minimalist Style)
# ==========================================
def alive_panel(_):
    buttons = [
        [
            # Paired Boxes
            InlineKeyboardButton(text="❄️ ADD ME ❄️", url=f"https://t.me/{app.username}?startgroup=true"),
            InlineKeyboardButton(text="❄️ SUPPORT ❄️", url=config.SUPPORT_GROUP),
        ],
        [
            # Full Width Box
            InlineKeyboardButton(text="ッ OWNER ッ", url=f"tg://openmessage?user_id={config.OWNER_ID}"),
        ]
    ]
    return buttons


# ==========================================
# 4. MUSIC HELP PANEL
# ==========================================
def music_start_panel(_):
    buttons = [
        [
            # Paired Boxes
            InlineKeyboardButton(text="🚀 GET HELP 🚀", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="🛠 TOOLS", callback_data="settings_helper"),
        ],
        [
            # Full Width Box
            InlineKeyboardButton(text="✨ SUPPORT CHAT ✨", url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons

# ---------------------------------------------------------------------------------
# ❤️ Powered by VIP MUSIC Team
# ---------------------------------------------------------------------------------
