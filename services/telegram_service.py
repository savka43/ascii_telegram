from io import BytesIO

from aiogram import Bot
from aiogram.types import BufferedInputFile, Message, PhotoSize

from utils.image import open_image


class TelegramFileService:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def download_photo(self, photo: PhotoSize) -> bytes:
        file = await self.bot.get_file(photo.file_id)
        buffer = BytesIO()
        await self.bot.download_file(file.file_path, destination=buffer)
        return buffer.getvalue()

    async def photo_to_image(self, photo: PhotoSize):
        data = await self.download_photo(photo)
        return open_image(BytesIO(data))


def png_input_file(data: bytes, filename: str = "ascii_art.png") -> BufferedInputFile:
    return BufferedInputFile(data, filename=filename)


def txt_input_file(data: bytes, filename: str = "ascii_art.txt") -> BufferedInputFile:
    return BufferedInputFile(data, filename=filename)


def get_result_file_id(message: Message) -> str:
    if message.photo:
        return message.photo[-1].file_id
    if message.document:
        return message.document.file_id
    raise ValueError("Message does not contain a result file")
