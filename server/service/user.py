from sqlalchemy.ext.asyncio import AsyncSession

from repository.user import UserRepository


class UserService:
    @staticmethod
    async def check_users(session: AsyncSession) : return await UserRepository.list_user(session)