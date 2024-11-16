import asyncio
import os
import logging
import imgkit
import io
import tempfile

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BufferedInputFile, CallbackQuery
from aiogram.filters import Command
from ascii_magic import AsciiArt
from PIL import Image
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
from handlers.handlers import start_router
from kbds import inline_keyboard

def resize_ascii(image):

    width, height = image.size
    cropped_image = image.crop((10, 10, width-10, height-10))

    return cropped_image


def ascii_art(image, cvet):
    my_art = AsciiArt.from_pillow_image(image)

    # Создаем временные файлы для HTML и изображения
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_input, \
        tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_output:
        tmp_path_in = tmp_input.name
        tmp_path_out = tmp_output.name

    # Генерация ASCII-арта и сохранение в HTML-файл с черным фоном
    my_art.to_html_file(
        path=tmp_path_in,
        width_ratio=1.5,
        columns=350,
        monochrome=cvet,
        styles = """
        display: block;
        border-width: 0px 0px;
        border-style: none;
        background-color: black;
        border-color: white;
        font-size: 8px;
        outline: none;
    """
    )

    # Конвертируем HTML-файл в изображение
    imgkit.from_file(tmp_path_in, tmp_path_out)

    # Открываем изображение ASCII-арта и применяем resize
    with Image.open(tmp_path_out) as ascii_image:
        resized_image = resize_ascii(ascii_image)

        # Сохраняем результат в BytesIO для отправки через Telegram
        output = io.BytesIO()
        resized_image.save(output, format="PNG")
        output.seek(0)

    # Удаляем временные файлы
    os.remove(tmp_path_in)
    os.remove(tmp_path_out)


    return output

ALLOWED_UPDATES = ["message", "edited_message", "callback_query"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
dp.include_router(start_router)

@dp.message(F.photo)
async def ask_art_type(message: types.Message):
    # Получаем самое качественное фото
    photo_data = message.photo[-1]
    
    # Отправляем фото с инлайн-кнопками, но не используя reply_to_message
    await message.answer_photo(
        photo=photo_data.file_id,
        reply_markup=inline_keyboard.inline_kb.as_markup()
    )


# Обработчик CallbackQuery и генерации арта
@dp.callback_query()
async def process_art_query(callback_query: CallbackQuery):
    await callback_query.answer()

    # Получаем фото из callback (последняя отправленная фотография)
    photo = callback_query.message.photo[-1]
    file_id = photo.file_id
    
    # Получаем путь к файлу фото
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Загружаем фотографию
    file_bytes = io.BytesIO()
    await bot.download_file(file_path, destination=file_bytes)
    file_bytes.seek(0)
    image = Image.open(file_bytes)

    # В зависимости от того, какую кнопку нажал пользователь
    if callback_query.data == "html_art":
        # Обработка для HTML-арта
        ascii_image = ascii_art(image, False)
        input_file = BufferedInputFile(ascii_image.getvalue(), filename="html_art.png")
        await callback_query.message.answer_photo(input_file)
        await callback_query.message.answer_document(input_file)

    elif callback_query.data == "ascii_art":
        # Обработка для ASCII-арта
        ascii_image = ascii_art(image, True)
        input_file = BufferedInputFile(ascii_image.getvalue(), filename="ascii_art.png")
        await callback_query.message.answer_photo(input_file)
        await callback_query.message.answer_document(input_file)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
