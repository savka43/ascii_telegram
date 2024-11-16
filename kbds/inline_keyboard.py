from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

inline_kb = InlineKeyboardBuilder()
inline_kb.row(InlineKeyboardButton(text="colored_ascii", callback_data="html_art"),
              InlineKeyboardButton(text="monochrome_ascii", callback_data="ascii_art"))

