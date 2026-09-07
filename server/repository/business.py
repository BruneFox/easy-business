from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from model import Busisness

class BusinessRepository:
    @staticmethod
    async def create(session: AsyncSession,name:str, user_id:int):
        busis_db = Busisness(business_name=name, id_boss=user_id)
        session.add(busis_db)
        await session.commit()
        return busis_db

    @staticmethod
    async def watch(session: AsyncSession,user_id: int):
        query = select(Busisness).where(Busisness.id_boss == user_id)
        result = await session.execute(query)
        user_b = result.scalars().all()
        result_arr = []
        for i in user_b:
            result_arr.append({
                "id": i.id,
                "lvl": i.lvl,
                "business_name": i.business_name,
                "warehouse": i.warehouse,
                "product": i.product
            })
        return result_arr