import json
import os

# FIRST: Import logging to make sure 'logger' and 'LOGGER' are available immediately
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
# Note: These modules must NOT import "logger" from "VIPMUSIC" directly.
# They should import from "VIPMUSIC.logging"
from VIPMUSIC.core.bot import VIPBot
from VIPMUSIC.core.userbot import Userbot
from VIPMUSIC.core.youtube import vipboy

vipboy()

# FOURTH: Initialize the Bot Clients
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
