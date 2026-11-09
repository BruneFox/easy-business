from typing import  AsyncGenerator
import jwt
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from model import async_session_maker
from repository.admin import AdminRepository
from config import settings

SECRET_KEY = settings.secret_key
bearer_scheme = HTTPBearer(auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session

async def get_active_user(session: AsyncSession, user_id:int):
    user = await AdminRepository.one_user(session,user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Ваш акаунт заблоковано адміністратором!")
    return user

async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        session: AsyncSession = Depends(get_db)
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Токен не знайдено")

    token = credentials.credentials
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
    return user

