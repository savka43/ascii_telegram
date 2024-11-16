from aiogram import Router, types
from aiogram.filters import Command

from kbds import reply_keyboard

start_router = Router()


@start_router.message(Command("start"))
async def cmd(message: types.Message):
    await message.answer("Привет! Это бот, который рисует ASCII-картинки\n Чтобы начать рисовать просто скинь мне картинку",
                         reply_markup=reply_keyboard.kb.as_markup())

@start_router.message(Command("donate"))
async def donations(message: types.Message):
    await message.answer("https://www.donationalerts.com/r/fluppyoooooooooo")

@start_router.message(Command("github"))
async def github(message: types.Message):
    await message.answer("https://github.com/savka43")
