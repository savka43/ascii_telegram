from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Черно-белый", callback_data="ascii:mode:bw"),
                InlineKeyboardButton(text="Цветной", callback_data="ascii:mode:color"),
            ],
        ],
    )


def width_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="80", callback_data="ascii:width:80"),
                InlineKeyboardButton(text="100", callback_data="ascii:width:100"),
                InlineKeyboardButton(text="120", callback_data="ascii:width:120"),
            ],
        ],
    )


def result_keyboard(art_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить TXT", callback_data=f"art:txt:{art_id}")],
            [
                InlineKeyboardButton(text="Повторить", callback_data=f"art:repeat:{art_id}"),
                InlineKeyboardButton(text="Мои арты", callback_data="history:page:0"),
            ],
        ],
    )
