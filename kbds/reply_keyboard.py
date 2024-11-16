from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb = ReplyKeyboardBuilder()
kb.add(KeyboardButton(text="/donate"),
       KeyboardButton(text="/github")
)

