from datetime import timedelta, timezone, datetime
from sqlalchemy.exc import IntegrityError
import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import SECRET_KEY
from repository.auth import AuthRepository
from schemas import UserData, UserLogin


class AuthService:
    @staticmethod
    async def create_new_user(
            session: AsyncSession,
            user: UserData,
    ):
        pasw_bytes = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        pasw_str = pasw_bytes.decode('utf-8')
        try:
            new_user = await AuthRepository.create(session, user.nickname, pasw_str, user.email)
            if new_user.id == 1:
                new_user.role = "Admin"
                session.add(new_user)
                await session.commit()
            return new_user
        except IntegrityError:
            await session.rollback()
            raise ValueError("Нікнейм вже зайнятий")

    @staticmethod
    async def check_user(
            session: AsyncSession,
            nickname: str,
            password: str,
    ):
        result = await AuthRepository.check(session,nickname)

        if not result:
            return None

        if result and result.is_banned:
            raise ValueError("Доступ заблоковано")

        check_paswus = password.encode('utf-8')
        check_paswdb = result.password.encode('utf-8')
        if bcrypt.checkpw(check_paswus, check_paswdb):
            payload = {
                "sub": result.nickname,
                "id": result.id,
                "role": result.role,
                "exp": datetime.now(timezone.utc) + timedelta(hours=24)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return token
        return None