from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def history_keyboard(art_id: int, offset: int, total: int) -> InlineKeyboardMarkup:
    prev_offset = max(0, offset - 1)
    next_offset = min(total - 1, offset + 1)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<", callback_data=f"history:page:{prev_offset}"),
                InlineKeyboardButton(text=">", callback_data=f"history:page:{next_offset}"),
            ],
            [InlineKeyboardButton(text="Отправить снова", callback_data=f"art:send:{art_id}")],
            [InlineKeyboardButton(text="Удалить", callback_data=f"art:delete:{art_id}:{offset}")],
        ],
    )
