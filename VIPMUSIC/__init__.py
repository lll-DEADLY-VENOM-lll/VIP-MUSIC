import asyncio
import json
import os
import uvloop

# --- सबसे पहले Event Loop को सेटअप करें ---
uvloop.install()
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ---------------------------------------

# अब बाकी के Imports करें
from .logging import logger, LOGGER

from VIPMUSIC.core.dir import dirr
from VIPMUSIC.core.git import git
from VIPMUSIC.misc import dbb, heroku, sudo

# Directories और Setup
dirr()
git()
dbb()
heroku()
sudo()

# Core Components को Import करें
from VIPMUSIC.core.bot import VIPBot
from VIPMUSIC.core.userbot import Userbot
from VIPMUSIC.core.youtube import vipboy

vipboy()

# अब Bots को Initialize करें (अब एरर नहीं आएगा)
app = VIPBot()
userbot = Userbot()

# Platforms Setup
from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()

HELPABLE = {}
