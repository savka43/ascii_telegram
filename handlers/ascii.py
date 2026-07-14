import logging
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.engine import session_factory
from keyboards.ascii import mode_keyboard, result_keyboard, width_keyboard
from services.ascii_service import AsciiService
from services.history_service import HistoryService
from services.telegram_service import (
    get_result_file_id,
    png_input_file,
    txt_input_file,
)
from states.ascii import AsciiGeneration
from utils.image import open_image


logger = logging.getLogger(__name__)
router = Router()
ascii_service = AsciiService()


@router.message(F.photo)
async def receive_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    await state.set_state(AsciiGeneration.choosing_mode)
    await state.update_data(source_file_id=photo.file_id)
    await message.answer("Выбери режим:", reply_markup=mode_keyboard())


@router.callback_query(AsciiGeneration.choosing_mode, F.data.startswith("ascii:mode:"))
async def choose_mode(callback: CallbackQuery, state: FSMContext) -> None:
    mode = callback.data.split(":")[-1]
    await state.update_data(mode=mode)
    await state.set_state(AsciiGeneration.choosing_width)
    await callback.message.edit_text("Выбери ширину ASCII:", reply_markup=width_keyboard())
    await callback.answer()


@router.callback_query(AsciiGeneration.choosing_width, F.data.startswith("ascii:width:"))
async def choose_width(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    width = int(callback.data.split(":")[-1])
    data = await state.get_data()
    source_file_id = data["source_file_id"]
    mode = data["mode"]
    await state.clear()

    await callback.message.edit_text("Генерирую ASCII...")
    try:
        await generate_and_send(
            bot=bot,
            target=callback.message,
            telegram_user=callback.from_user,
            source_file_id=source_file_id,
            mode=mode,
            width=width,
            save_to_history=True,
        )
    except Exception:
        logger.exception("Failed to generate ASCII art")
        await callback.message.answer("Не получилось обработать изображение. Попробуй другое фото.")
    await callback.answer()


@router.callback_query(F.data.startswith("art:txt:"))
async def send_txt(callback: CallbackQuery, bot: Bot) -> None:
    art_id = int(callback.data.split(":")[-1])
    async with session_factory() as session:
        art = await HistoryService(session).get_art(callback.from_user, art_id)

    if art is None:
        await callback.answer("Арт не найден", show_alert=True)
        return

    image = await download_source_image(bot, art.source_file_id)
    result = ascii_service.convert(image=image, mode=art.mode, width=art.width)
    await callback.message.answer_document(
        txt_input_file(ascii_service.render_txt(result), filename=f"ascii_art_{art.id}.txt")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("art:repeat:"))
async def repeat_art(callback: CallbackQuery, bot: Bot) -> None:
    art_id = int(callback.data.split(":")[-1])
    async with session_factory() as session:
        art = await HistoryService(session).get_art(callback.from_user, art_id)

    if art is None:
        await callback.answer("Арт не найден", show_alert=True)
        return

    await callback.message.answer("Повторяю генерацию...")
    await generate_and_send(
        bot=bot,
        target=callback.message,
        telegram_user=callback.from_user,
        source_file_id=art.source_file_id,
        mode=art.mode,
        width=art.width,
        save_to_history=True,
    )
    await callback.answer()


async def generate_and_send(
    bot: Bot,
    target: Message,
    telegram_user,
    source_file_id: str,
    mode: str,
    width: int,
    save_to_history: bool,
) -> None:
    image = await download_source_image(bot, source_file_id)
    result = ascii_service.convert(image=image, mode=mode, width=width)
    png_data = ascii_service.render_png(result)

    result_message = await target.answer_photo(
        png_input_file(png_data),
        caption=build_result_caption(mode, width),
    )
    result_file_id = get_result_file_id(result_message)

    if save_to_history:
        async with session_factory() as session:
            art = await HistoryService(session).save_art(
                telegram_user=telegram_user,
                source_file_id=source_file_id,
                result_file_id=result_file_id,
                mode=mode,
                width=width,
            )
        await result_message.edit_reply_markup(reply_markup=result_keyboard(art.id))


async def download_source_image(bot: Bot, file_id: str):
    file = await bot.get_file(file_id)
    buffer = BytesIO()
    await bot.download_file(file.file_path, destination=buffer)
    buffer.seek(0)
    return open_image(buffer)


def build_result_caption(mode: str, width: int) -> str:
    mode_title = "Цветной" if mode == "color" else "Черно-белый"
    return f"Готово\n\nРежим: {mode_title}\nШирина: {width}"
