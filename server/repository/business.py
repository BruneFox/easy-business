from sentry_sdk.worker import Worker
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from model import Busisness
from model import User
from sqlalchemy.orm import selectinload


class BusinessRepository:
    @staticmethod
    async def search_user(session: AsyncSession, user_id:int):
        user = select(User).where(User.id == user_id)
        result = await session.execute(user)
        user_res = result.scalar_one_or_none()
        return user_res

    @staticmethod
    async def search_business(session: AsyncSession,business_id, user_id: int):
        bis = select(User,Busisness).where(and_(User.id == user_id, Busisness.id == business_id, Busisness.id_boss == User.id))
        result = await session.execute(bis)
        bis_res = result.one_or_none()
        return bis_res

    @staticmethod
    async def create(session: AsyncSession,name:str, user_id:int):
        busis_db = Busisness(business_name=name, id_boss=user_id)
        session.add(busis_db)
        return busis_db

    @staticmethod
    async def watch(session: AsyncSession,user_id: int):
        query = select(Busisness).where(Busisness.id_boss == user_id).order_by(Busisness.id)
        result = await session.execute(query)
        return result.scalars().all()