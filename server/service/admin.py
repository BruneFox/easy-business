from sqlalchemy.ext.asyncio import AsyncSession

from repository.admin import AdminRepository


class AdminService:
    @staticmethod
    async def check_users(session: AsyncSession) :
        users = await AdminRepository.list_user(session)
        result_arr=[]
        for i in users:
            result_arr.append({
                "id": i.id,
                "nickname": i.nickname,
                "email": i.email,
                "role": i.role,
                "is_banned": i.is_banned,
                "money": i.money
            })
        return result_arr

    @staticmethod
    async def ban(session: AsyncSession,id:int):
        killer = await AdminRepository.one_user(session,id)
        if killer:
            killer.is_banned = not killer.is_banned
            session.add(killer)
            await session.commit()
            return killer
        else:
            raise ValueError("Користувача з таким id не існує")

    @staticmethod
    async def change_m(session: AsyncSession,id:int,cash:int):
        user = await AdminRepository.one_user(session,id)
        if user:
            user.money += cash
            session.add(user)
            await session.commit()
            return user
        else:
            raise ValueError("Користувача з таким id не існує")

    @staticmethod
    async def admin(session: AsyncSession, id: int):
        user = await AdminRepository.one_user(session, id)
        if user:
            user.role = "Admin"
            session.add(user)
            await session.commit()
            return user
        else:
            raise ValueError("Користувача з таким id не існує")
