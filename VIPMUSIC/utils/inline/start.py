from pyrogram.types import InlineKeyboardButton
import config
from VIPMUSIC import app

def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ADD ME TO YOUR GROUP ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="⚜️ LANGUAGE", callback_data="LG"),
            InlineKeyboardButton(text="🛡️ POLICY", url=config.UPSTREAM_REPO),
        ],
        [
            InlineKeyboardButton(text="📩 CHANNEL ↗", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="📩 SUPPORT ↗", url=config.SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(
                text="🔍 HOW TO USE? COMMAND MENU", callback_data="settings_back_helper"
            ),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ADD ME TO YOUR GROUP ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="⚜️ LANGUAGE", callback_data="LG"),
            InlineKeyboardButton(text="🛡️ POLICY", url=config.UPSTREAM_REPO),
        ],
        [
            InlineKeyboardButton(text="📩 CHANNEL ↗", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="📩 SUPPORT ↗", url=config.SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(
                text="🔍 HOW TO USE? COMMAND MENU", callback_data="settings_back_helper"
            ),
        ],
    ]
    return buttons

def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(text="⚜️ LANGUAGE", callback_data="LG"),
            InlineKeyboardButton(text="🛡️ POLICY", url=config.UPSTREAM_REPO),
        ],
        [
            InlineKeyboardButton(text="📩 SUPPORT ↗", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text="➕ ADD ME ➕", url=f"https://t.me/{app.username}?startgroup=true"),
        ],
    ]
    return buttons
