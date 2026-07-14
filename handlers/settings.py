from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message


router = Router()
user_settings: dict[int, dict[str, str | int]] = {}


def settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    settings = user_settings.setdefault(
        user_id,
        {"width": 100, "mode": "bw", "format": "PNG"},
    )
    mode_title = "Цветной" if settings["mode"] == "color" else "Черно-белый"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="80", callback_data="settings:width:80"),
                InlineKeyboardButton(text="100", callback_data="settings:width:100"),
                InlineKeyboardButton(text="120", callback_data="settings:width:120"),
            ],
            [
                InlineKeyboardButton(text="Черно-белый", callback_data="settings:mode:bw"),
                InlineKeyboardButton(text="Цветной", callback_data="settings:mode:color"),
            ],
            [
                InlineKeyboardButton(text="PNG", callback_data="settings:format:PNG"),
                InlineKeyboardButton(text="TXT", callback_data="settings:format:TXT"),
            ],
            [
                InlineKeyboardButton(
                    text=f"Сейчас: {settings['width']} / {mode_title} / {settings['format']}",
                    callback_data="settings:noop",
                )
            ],
        ]
    )


@router.message(Command("settings"))
@router.message(F.text == "Настройки")
async def settings_command(message: Message) -> None:
    await message.answer("Настройки:", reply_markup=settings_keyboard(message.from_user.id))


@router.callback_query(F.data.startswith("settings:"))
async def update_settings(callback: CallbackQuery) -> None:
    parts = callback.data.split(":", maxsplit=2)
    key = parts[1]
    if key == "noop":
        await callback.answer()
        return
    value = parts[2]

    settings = user_settings.setdefault(
        callback.from_user.id,
        {"width": 100, "mode": "bw", "format": "PNG"},
    )
    settings[key] = int(value) if key == "width" else value
    await callback.message.edit_reply_markup(reply_markup=settings_keyboard(callback.from_user.id))
    await callback.answer("Сохранено")
