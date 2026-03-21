import asyncio
import uvloop

# 1. सबसे पहले uvloop Policy सेट करें (यह RuntimeError को रोकने के लिए जरूरी है)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# 2. एक नया लूप बनाएं और उसे सेट करें
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# 3. अब Logger और बाकी चीजें इम्पोर्ट करें
from .logging import LOGGER
logger = LOGGER 

# HELPABLE डिक्शनरी
HELPABLE = {}

# 4. बेसिक सेटअप फंक्शन्स लोड करें
from VIPMUSIC.core.dir import dirr
from VIPMUSIC.core.git import git
from VIPMUSIC.misc import dbb, heroku, sudo

dirr()
git()
dbb()
heroku()
sudo()

# 5. अब Bot और Userbot क्लास लोड करें
from VIPMUSIC.core.bot import VIPBot
from VIPMUSIC.core.userbot import Userbot

# यहाँ बॉट शुरू होगा
app = VIPBot()
userbot = Userbot()

# 6. Platforms सेटअप
from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
