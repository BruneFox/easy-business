from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_db, get_current_admin
from service.admin import AdminService
from schemas import ChangeMoney

router = APIRouter(prefix="/api/users", tags=["users"])




@router.get("")
async def get_user(session: AsyncSession = Depends(get_db),
                   admin: dict = Depends(get_current_admin)
                   ):
    return await AdminService.check_users(session)

@router.post("/{user_id}/ban")
async def ban_user(
                   user_id: int,
                   session: AsyncSession = Depends(get_db),
                   admin: dict = Depends(get_current_admin)
                   ):
    user_ban = await AdminService.ban(session,user_id)
    ban_status = "Заблоковано" if user_ban.is_banned else "Розблоковано"
    return {'message':f'Користувача {user_ban.nickname} {ban_status}'}

@router.post("/{user_id}/balance-adjustments")
async def change_money(
        user_id: int,
        count_money: ChangeMoney,
        session: AsyncSession = Depends(get_db),
        admin: dict = Depends(get_current_admin)
):
    user_change = await AdminService.change_m(session, user_id,count_money.cash)
    return {'message': f'У користувача {user_change.nickname} тепер {user_change.money} коштів' }


@router.post("/{user_id}/role")
async def give_admin(
                   user_id: int,
                   session: AsyncSession = Depends(get_db),
                   admin: dict = Depends(get_current_admin)
                   ):

    user_admin = await AdminService.admin(session,user_id)
    return {'message':f'Роль видано для {user_admin.nickname} '}
