from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main import main_keyboard


router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет!\n\n"
        "Отправь мне изображение и я превращу его в ASCII.\n\n"
        "Также ты можешь посмотреть историю своих работ.",
        reply_markup=main_keyboard(),
    )
