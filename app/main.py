import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from database.engine import create_db
from handlers import ascii_router, history_router, settings_router, start_router


ALLOWED_UPDATES = ["message", "callback_query"]


async def main() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    await create_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(ascii_router)
    dp.include_router(history_router)
    dp.include_router(settings_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


def run() -> None:
    asyncio.run(main())
