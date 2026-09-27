from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_db, get_current_user, SECRET_KEY
from schemas import UserData, UserLogin
from service.auth import AuthService

router = APIRouter()


@router.post("/register")
async def register_page(
        user: UserData,
        session: AsyncSession = Depends(get_db)):
    try:
        new_user = await AuthService.create_new_user(session, user)
        return {"message": "Користувач зареєструвався!", "nickname": new_user.nickname}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@router .post("/login")
async def login_page(
        userforcheck: UserLogin,
        session: AsyncSession = Depends(get_db)):
    try:
        token = await AuthService.check_user(session, userforcheck.nickname, userforcheck.password)
        if not token:
            raise HTTPException(status_code=401, detail="Неправильний логін та/або пароль")
        return {"message": "Користувач війшов", "access_token": token}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")