from pyrogram.types import InlineKeyboardButton

import config
from config import SUPPORT_GROUP
from VIPMUSIC import app


def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="⌁ Add To Group ⌁",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton("⧉ Commands", callback_data="settings_back_helper"),
            InlineKeyboardButton("⧉ Settings", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton("⌁ Support ⌁", url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="⌁ Invite ⌁",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton("⧉ Group", url=config.SUPPORT_GROUP),
            InlineKeyboardButton("⧉ Channel", url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton("⌁ Features ⌁", callback_data="settings_back_helper")
        ],
    ]
    return buttons


def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="⌁ Add ⌁",
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(
                text="⌁ Support ⌁",
                url=f"{SUPPORT_GROUP}"
            ),
        ],
    ]
    return buttons


def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="⌁ Start Bot ⌁",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton("⧉ About", callback_data="about"),
            InlineKeyboardButton("⧉ Support", callback_data="support"),
        ],
        [
            InlineKeyboardButton("⌁ Features ⌁", callback_data="feature")
        ],
    ]
    return buttons
