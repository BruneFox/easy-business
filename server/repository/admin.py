from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model import User


class AdminRepository:
    @staticmethod
    async def list_user(session: AsyncSession):
        s = await session.execute(select(User).order_by(User.id))
        users = s.scalars().all()
        return users
    @staticmethod
    async def one_user(session: AsyncSession, id_user: int):
        bad_user = await session.execute(select(User).where(User.id == id_user))
        head_user = bad_user.scalar_one_or_none()
        return head_user