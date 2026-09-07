import os
from typing import  AsyncGenerator
import jwt
from dotenv import load_dotenv
from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from model import async_session_maker

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default_fallback_key")


async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Токен не знайдено")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token,SECRET_KEY ,algorithms = ['HS256'])
        return {"nickname": payload.get("sub"), "id": payload.get("id")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Закінчився час сесії")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невірний токен")


async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session