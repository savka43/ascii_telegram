from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Art
from database.repositories import ArtRepository, UserRepository


class HistoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.arts = ArtRepository(session)

    async def save_art(
        self,
        telegram_user: TelegramUser,
        source_file_id: str,
        result_file_id: str,
        mode: str,
        width: int,
    ) -> Art:
        user = await self.users.get_or_create(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
        )
        art = await self.arts.create(
            user_id=user.id,
            source_file_id=source_file_id,
            result_file_id=result_file_id,
            mode=mode,
            width=width,
        )
        await self.session.commit()
        return art

    async def get_page(self, telegram_user: TelegramUser, offset: int) -> tuple[Art | None, int]:
        user = await self.users.get_or_create(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
        )
        total = await self.arts.count_by_user(user.id)
        if total == 0:
            await self.session.commit()
            return None, 0

        safe_offset = min(max(offset, 0), total - 1)
        art = await self.arts.get_by_user_offset(user.id, safe_offset)
        await self.session.commit()
        return art, total

    async def get_art(self, telegram_user: TelegramUser, art_id: int) -> Art | None:
        user = await self.users.get_or_create(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
        )
        art = await self.arts.get_by_id_for_user(art_id, user.id)
        await self.session.commit()
        return art

    async def delete_art(self, telegram_user: TelegramUser, art_id: int) -> bool:
        user = await self.users.get_or_create(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
        )
        deleted = await self.arts.delete_for_user(art_id, user.id)
        await self.session.commit()
        return deleted
