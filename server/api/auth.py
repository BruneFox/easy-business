from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_db
from schemas import UserData, UserLogin
from service.auth import AuthService

router = APIRouter()

@router.post("/api/auth/register", status_code=201)
async def register_page(user: UserData, session: AsyncSession = Depends(get_db)):
        new_user = await AuthService.create_new_user(session, user)
        return {"message": "Користувач зареєструвався!", "nickname": new_user.nickname}


@router.post("/api/auth/login")
async def login_page(userforcheck: UserLogin,session: AsyncSession = Depends(get_db)):
        token = await AuthService.check_user(session, userforcheck.nickname, userforcheck.password)
        return {"message": "Користувач війшов", "access_token": token}