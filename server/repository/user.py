from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model import User


class UserRepository:
    @staticmethod
    async def list_user(session: AsyncSession):
        s = await session.execute(select(User))
        users = s.scalars().all()

        result_arr=[]
        for i in users:
            result_arr.append({
                "id": i.id,
                "nickname": i.nickname,
                "email": i.email
            })
        return result_arr