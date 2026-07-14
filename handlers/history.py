from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from database.engine import session_factory
from database.models import Art
from keyboards.history import history_keyboard
from services.history_service import HistoryService


router = Router()


@router.message(Command("history"))
@router.message(F.text == "Мои арты")
async def history_command(message: Message) -> None:
    await show_history_message(message, offset=0)


@router.callback_query(F.data.startswith("history:page:"))
async def history_page(callback: CallbackQuery) -> None:
    offset = int(callback.data.split(":")[-1])
    await show_history_message(callback.message, offset=offset, user=callback.from_user)
    await callback.answer()


@router.callback_query(F.data.startswith("art:send:"))
async def send_saved_art(callback: CallbackQuery) -> None:
    art_id = int(callback.data.split(":")[-1])
    async with session_factory() as session:
        art = await HistoryService(session).get_art(callback.from_user, art_id)

    if art is None:
        await callback.answer("Арт не найден", show_alert=True)
        return

    await callback.message.answer_photo(art.result_file_id, caption=build_art_caption(art, 0, 1))
    await callback.answer()


@router.callback_query(F.data.startswith("art:delete:"))
async def delete_saved_art(callback: CallbackQuery) -> None:
    _, _, art_id, offset = callback.data.split(":")
    async with session_factory() as session:
        deleted = await HistoryService(session).delete_art(callback.from_user, int(art_id))

    if not deleted:
        await callback.answer("Арт не найден", show_alert=True)
        return

    await callback.answer("Удалено")
    await show_history_message(callback.message, offset=max(0, int(offset) - 1), user=callback.from_user)


async def show_history_message(message: Message, offset: int, user=None) -> None:
    telegram_user = user or message.from_user
    async with session_factory() as session:
        art, total = await HistoryService(session).get_page(telegram_user, offset)

    if art is None:
        await message.answer("История пока пустая.")
        return

    safe_offset = min(max(offset, 0), total - 1)
    await message.answer_photo(
        art.result_file_id,
        caption=build_art_caption(art, safe_offset, total),
        reply_markup=history_keyboard(art.id, safe_offset, total),
    )


def build_art_caption(art: Art, offset: int, total: int) -> str:
    mode_title = "Цветной" if art.mode == "color" else "Черно-белый"
    created = art.created_at.strftime("%d.%m.%Y")
    return (
        f"Арт {offset + 1} из {total}\n\n"
        f"Создан:\n{created}\n\n"
        f"Ширина:\n{art.width}\n\n"
        f"Режим:\n{mode_title}"
    )
