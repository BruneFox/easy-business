from typing import  AsyncGenerator
import jwt
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from model import async_session_maker
from repository.user import UserRepository
from config import settings

SECRET_KEY = settings.secret_key

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session

async def get_active_user(session: AsyncSession, user_id:int):
    user = await UserRepository.one_user(session,user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Ваш акаунт заблоковано адміністратором!")
    return user

async def get_current_user(
        authorization: str = Header(None),
        session: AsyncSession = Depends(get_db)
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Токен не знайдено")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Невірний формат токена")

    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get("id")
        user = await get_active_user(session, user_id)
        return {"nickname": user.nickname, "id": user.id, "role": user.role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Закінчився час сесії")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невірний токен")

async def get_current_admin(
        user: dict = Depends(get_current_user)
):
    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено!")

