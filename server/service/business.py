from sqlalchemy.ext.asyncio import AsyncSession
from repository.business import BusinessRepository
from schemas import BusinessData


class BusinessService:
    @staticmethod
    async def buy_new_business(
            session: AsyncSession,
            bis_data: BusinessData,
            user_id: int):
        return await BusinessRepository.create(session, bis_data.name,user_id)

    @staticmethod
    async def watch_user_business(
            session: AsyncSession,
            user_id:int):
        return await BusinessRepository.watch(session, user_id)