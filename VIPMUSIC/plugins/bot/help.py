import re
from math import ceil
from typing import Union

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BANNED_USERS, START_IMG_URL
from strings import get_command, get_string
from VIPMUSIC import HELPABLE, app
from VIPMUSIC.utils.database import get_lang, is_commanddelete_on
from VIPMUSIC.utils.decorators.language import LanguageStart

### Command Settings
HELP_COMMAND = get_command("HELP_COMMAND")

COLUMN_SIZE = 4  
NUM_COLUMNS = 3  

def get_small_caps(text):
    small_caps_map = {
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ғ", "g": "ɢ", "h": "ʜ",
        "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ",
        "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
        "y": "ʏ", "z": "ᴢ",
    }
    return "".join(small_caps_map.get(char.lower(), char) for char in text)

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other): return self.text == other.text
    def __lt__(self, other): return self.text < other.text
    def __gt__(self, other): return self.text > other.text

def paginate_modules(page_n, module_dict, prefix, chat=None, close: bool = False):
    # Modules sorting A to Z
    sorted_modules = sorted(module_dict.values(), key=lambda x: x.__MODULE__.lower())
    
    modules = []
    for x in sorted_modules:
        module_name = get_small_caps(x.__MODULE__)
        if not chat:
            callback_data = "{}_module({},{})".format(prefix, x.__MODULE__.lower(), page_n)
        else:
            callback_data = "{}_module({},{},{})".format(prefix, chat, x.__MODULE__.lower(), page_n)
        
        modules.append(EqInlineKeyboardButton(module_name, callback_data=callback_data))

    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]
    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    get_small_caps("Prev"),
                    callback_data="{}_prev({})".format(prefix, modulo_page - 1 if modulo_page > 0 else max_num_pages - 1),
                ),
                EqInlineKeyboardButton(
                    get_small_caps("Home") if not close else get_small_caps("Close"),
                    callback_data="settingsback_helper" if not close else "close",
                ),
                EqInlineKeyboardButton(
                    get_small_caps("Next"),
                    callback_data="{}_next({})".format(prefix, modulo_page + 1),
                ),
            )
        ]
    else:
        pairs.append(
            [
                EqInlineKeyboardButton(
                    get_small_caps("Home") if not close else get_small_caps("Close"),
                    callback_data="settingsback_helper" if not close else "close",
                ),
            ]
        )
    return pairs

@app.on_message(filters.command(HELP_COMMAND) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(client: app, update: Union[types.Message, types.CallbackQuery]):
    is_callback = isinstance(update, types.CallbackQuery)
    
    # Premium Small Caps Text
    text = (
        f"✨ **{get_small_caps('ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ')}** ✨\n\n"
        f"⚡ {get_small_caps('sᴇʟᴇᴄᴛ ᴀ ᴍᴏᴅᴜʟᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.')}\n\n"
        f"💌 {get_small_caps('ɪғ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ᴅᴏᴜʙᴛ, ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ᴀsᴋ ɪɴ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ.')}"
    )

    if is_callback:
        try: await update.answer()
        except: pass
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
        await update.edit_message_text(text, reply_markup=keyboard)
    else:
        if await is_commanddelete_on(update.chat.id):
            try: await update.delete()
            except: pass
        
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
        if START_IMG_URL:
            await update.reply_photo(photo=START_IMG_URL, caption=text, reply_markup=keyboard)
        else:
            await update.reply_text(text=text, reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client, query):
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back\((\d+)\)", query.data)
    
    main_menu_text = (
        f"✨ **{get_small_caps('ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ')}** ✨\n\n"
        f"💌 {get_small_caps('sᴇʟᴇᴄᴛ ᴀ ᴍᴏᴅᴜʟᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.')}"
    )
    
    if mod_match:
        module_key = mod_match.group(1)
        prev_page_num = int(mod_match.group(2))
        module_name = get_small_caps(HELPABLE[module_key].__MODULE__)
        
        text = (
            f"👀 **{get_small_caps('ᴍᴏᴅᴜʟᴇ')}: {module_name}**\n\n"
            f"{HELPABLE[module_key].__HELP__}\n\n"
            f"✨ {get_small_caps('ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴠɪᴘ ᴍᴜsɪᴄ')}"
        )

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=get_small_caps("Back"), callback_data=f"help_back({prev_page_num})"),
                    InlineKeyboardButton(text=get_small_caps("Close"), callback_data="close"),
                ],
            ]
        )
        await query.message.edit(text=text, reply_markup=key)

    elif prev_match or next_match or back_match:
        curr_page = int((prev_match or next_match or back_match).group(1))
        await query.message.edit(text=main_menu_text, reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page, HELPABLE, "help")))

    await client.answer_callback_query(query.id)
