#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.

# 1. सबसे पहले Logger को लोड करें ताकि बाकी मॉड्यूल्स इसे इस्तेमाल कर सकें
from .logging import LOGGER

# कई फाइलें 'logger' (small letters) ढूंढती हैं, इसलिए यह जरूरी है
logger = LOGGER 

# 2. HELPABLE डिक्शनरी को शुरू में ही डिफाइन करें
HELPABLE = {}

# 3. बेसिक सेटअप फंक्शन्स लोड करें
from VIPMUSIC.core.dir import dirr
from VIPMUSIC.core.git import git
from VIPMUSIC.misc import dbb, heroku, sudo

# Directories सेटअप
dirr()

# Git अपडेट चेक करें
git()

# DB और Heroku सेटअप
dbb()
heroku()
sudo()

# 4. अब Bot और Userbot को लोड करें (Logger के बाद)
from VIPMUSIC.core.bot import VIPBot
from VIPMUSIC.core.userbot import Userbot

app = VIPBot()
userbot = Userbot()

# 5. सबसे आखिर में Platforms लोड करें
from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
