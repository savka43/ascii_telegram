from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Art, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, telegram_id: int, username: str | None) -> User:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            self.session.add(user)
            await self.session.flush()
            return user

        if user.username != username:
            user.username = username
            await self.session.flush()
        return user


class ArtRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: int,
        source_file_id: str,
        result_file_id: str,
        mode: str,
        width: int,
    ) -> Art:
        art = Art(
            user_id=user_id,
            source_file_id=source_file_id,
            result_file_id=result_file_id,
            mode=mode,
            width=width,
        )
        self.session.add(art)
        await self.session.flush()
        return art

    async def count_by_user(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Art.id)).where(Art.user_id == user_id)
        )
        return result.scalar_one()

    async def get_by_user_offset(self, user_id: int, offset: int) -> Art | None:
        result = await self.session.execute(
            select(Art)
            .where(Art.user_id == user_id)
            .order_by(Art.created_at.desc(), Art.id.desc())
            .offset(offset)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, art_id: int, user_id: int) -> Art | None:
        result = await self.session.execute(
            select(Art).where(Art.id == art_id, Art.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_for_user(self, art_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            delete(Art).where(Art.id == art_id, Art.user_id == user_id)
        )
        return result.rowcount > 0
