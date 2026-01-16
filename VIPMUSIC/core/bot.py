import asyncio
import threading
import uvloop
from flask import Flask
import pyrogram 
from pyrogram import Client, idle
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatWriteForbidden, PeerIdInvalid, FloodWait
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

import config
from ..logging import LOGGER

uvloop.install()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run():
    app.run(host="0.0.0.0", port=8000, debug=False)

class VIPBot(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            "VIPMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = get_me.first_name + " " + (get_me.last_name or "")
        self.mention = get_me.mention

        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏", url=f"https://t.me/{self.username}?startgroup=true")]]
        )

        if config.LOG_GROUP_ID:
            try:
                # जबरदस्ती ग्रुप को ढूँढना (Force Resolve)
                try:
                    await self.get_chat(config.LOG_GROUP_ID)
                except Exception:
                    pass

                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.START_IMG_URL,
                    caption=f"╔════❰𝐖𝐄𝐋𝐂𝐎𝐌𝐄❱════❍⊱❁۪۪\n║\n║┣⪼🥀𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐁𝐚𝐛𝐲🎉\n║\n║┣⪼ {self.name}\n║\n║┣⪼🎈𝐈𝐃:- `{self.id}` \n║\n║┣⪼🎄@{self.username} \n║ \n║┣⪼💖𝐓𝐡𝐚𝐧𝐤𝐬 𝐅𝐨𝐫 𝐔𝐬𝐢𝐧𝐠😍\n║\n╚════════════════❍⊱❁",
                    reply_markup=button,
                )
            except (PeerIdInvalid, Exception) as e:
                LOGGER(__name__).error(f"Log Group Error: {e}. Bot will continue starting...")
        
        # Commands setup (बिना किसी स्किप के)
        if config.SET_CMDS:
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "Start the bot"),
                        BotCommand("help", "Get the help menu"),
                        BotCommand("ping", "Check if the bot is alive or dead"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                        BotCommand("stop", "Stop the current song"),
                        BotCommand("pause", "Pause the current song"),
                        BotCommand("resume", "Resume the paused song"),
                        BotCommand("skip", "Skip the current song"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
            except Exception:
                pass

        LOGGER(__name__).info(f"MusicBot Started as {self.name}")

async def anony_boot():
    bot = VIPBot()
    await bot.start()
    await idle()

if __name__ == "__main__":
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    asyncio.run(anony_boot())
