import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from model import User


class AuthRepository:
    @staticmethod
    async def create(session: AsyncSession, nickname:str, password:str, email:str):
        user_db = User(nickname=nickname, email=email, password=password)
        session.add(user_db)
        await session.commit()
        return user_db

    @staticmethod
    async def check(session: AsyncSession, user_name: str):
        check_name = select(User).where(User.nickname == user_name)
        name_session = await session.execute(check_name)
        return name_session.scalar_one_or_none()