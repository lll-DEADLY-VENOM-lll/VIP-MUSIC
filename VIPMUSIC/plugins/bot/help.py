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

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other): return self.text == other.text
    def __lt__(self, other): return self.text < other.text
    def __gt__(self, other): return self.text > other.text

def paginate_modules(page_n, module_dict, prefix, chat=None, close: bool = False):
    # Modules ko A to Z sort kiya gaya hai
    sorted_module_keys = sorted(module_dict.keys(), key=lambda x: module_dict[x].__MODULE__)
    
    modules = []
    for key in sorted_module_keys:
        module_name = module_dict[key].__MODULE__
        # Ekdum simple text buttons
        button_text = f"{module_name}"
        
        if not chat:
            callback_data = "{}_module({},{})".format(prefix, key.lower(), page_n)
        else:
            callback_data = "{}_module({},{},{})".format(prefix, chat, key.lower(), page_n)
            
        modules.append(EqInlineKeyboardButton(button_text, callback_data=callback_data))

    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]
    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "Back",
                    callback_data="{}_prev({})".format(prefix, modulo_page - 1 if modulo_page > 0 else max_num_pages - 1),
                ),
                EqInlineKeyboardButton(
                    "Home" if not close else "Close",
                    callback_data="settingsback_helper" if not close else "close",
                ),
                EqInlineKeyboardButton(
                    "Next",
                    callback_data="{}_next({})".format(prefix, modulo_page + 1),
                ),
            )
        ]
    else:
        pairs.append(
            [
                EqInlineKeyboardButton(
                    "Home" if not close else "Close",
                    callback_data="settingsback_helper" if not close else "close",
                ),
            ]
        )
    return pairs

@app.on_message(filters.command(HELP_COMMAND) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(client: app, update: Union[types.Message, types.CallbackQuery]):
    is_callback = isinstance(update, types.CallbackQuery)
    
    # Clean and simple text
    text = (
        "**Bot Help Menu**\n\n"
        "Select a module from the buttons below to see the available commands."
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
        "**Bot Help Menu**\n\n"
        "Select a module from the buttons below to see the available commands."
    )
    
    if mod_match:
        module_key = mod_match.group(1)
        prev_page_num = int(mod_match.group(2))
        module_name = HELPABLE[module_key].__MODULE__
        
        text = (
            f"**Module: {module_name}**\n"
            f"--------------------------\n\n"
            f"{HELPABLE[module_key].__HELP__}\n\n"
            f"--------------------------"
        )

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Back", callback_data=f"help_back({prev_page_num})"),
                    InlineKeyboardButton(text="Close", callback_data="close"),
                ],
            ]
        )
        await query.message.edit(text=text, reply_markup=key)

    elif prev_match or next_match or back_match:
        curr_page = int((prev_match or next_match or back_match).group(1))
        await query.message.edit(text=main_menu_text, reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page, HELPABLE, "help")))

    await client.answer_callback_query(query.id)
