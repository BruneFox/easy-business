from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_db, get_current_admin
from service.user import UserService
from schemas import ChangeMoney

router = APIRouter()




@router.get("/users")
async def get_user(session: AsyncSession = Depends(get_db),
                   admin: dict = Depends(get_current_admin)
                   ):
    try:
        return await UserService.check_users(session)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@router.post("/ban_user/{user_id}")
async def ban_user(
                   user_id: int,
                   session: AsyncSession = Depends(get_db),
                   admin: dict = Depends(get_current_admin)
                   ):
    try:
        user_ban = await UserService.ban(session,user_id)
        ban_status = "Заблоковано" if user_ban.is_banned else "Розблоковано"
        return {'message':f'Користувача {user_ban.nickname} {ban_status}'}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@router.post("/change_money/{user_id}")
async def change_money(
        user_id: int,
        count_money: ChangeMoney,
        session: AsyncSession = Depends(get_db),
        admin: dict = Depends(get_current_admin)
):
    try:
        user_change = await UserService.change_m(session, user_id,count_money.cash)
        return {'message': f'У користувача {user_change.nickname} тепер {user_change.money} коштів' }
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@router.post("/give_admin/{user_id}")
async def give_admin(
                   user_id: int,
                   session: AsyncSession = Depends(get_db),
                   admin: dict = Depends(get_current_admin)
                   ):
    try:
        user_admin = await UserService.admin(session,user_id)
        return {'message':f'Роль видано для {user_admin.nickname} '}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")