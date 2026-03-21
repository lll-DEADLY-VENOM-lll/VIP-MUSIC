import asyncio
import uvloop

# 1. सबसे पहले uvloop को इनस्टॉल करें और Event Loop सेट करें
uvloop.install()

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# 2. अब Logger लोड करें
from .logging import LOGGER
logger = LOGGER 

# 3. HELPABLE डिक्शनरी
HELPABLE = {}

# 4. बेसिक सेटअप फंक्शन्स
from VIPMUSIC.core.dir import dirr
from VIPMUSIC.core.git import git
from VIPMUSIC.misc import dbb, heroku, sudo

dirr()
git()
dbb()
heroku()
sudo()

# 5. अब Bot और Userbot लोड करें
from VIPMUSIC.core.bot import VIPBot
from VIPMUSIC.core.userbot import Userbot

app = VIPBot()
userbot = Userbot()

# 6. Platforms लोड करें
from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
