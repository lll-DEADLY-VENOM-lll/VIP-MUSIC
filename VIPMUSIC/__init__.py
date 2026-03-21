import asyncio
import json
import os

# --- STEP 1: FIX EVENT LOOP ---
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

# Create and set the event loop manually for Python 3.10+
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ------------------------------

# FIRST: Import logging
from .logging import logger, LOGGER

# SECOND: Setup directories and environment
from VIPMUSIC.core.dir import dirr
from VIPMUSIC.core.git import git
from VIPMUSIC.misc import dbb, heroku, sudo

dirr()
git()
dbb()
heroku()
sudo()

# THIRD: Import core components
from VIPMUSIC.core.bot import VIPBot
from VIPMUSIC.core.userbot import Userbot
from VIPMUSIC.core.youtube import vipboy

vipboy()

# FOURTH: Initialize the Bot Clients
# (Now the loop exists, so this won't crash)
app = VIPBot()
userbot = Userbot()

# FIFTH: Initialize Platforms
from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()

HELPABLE = {}
