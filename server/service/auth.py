from datetime import timedelta, timezone, datetime
from sqlalchemy.exc import IntegrityError
import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import SECRET_KEY
from repository.auth import AuthRepository
from schemas import UserData, UserLogin
from exceptions import AppError, NotFoundError, ForbiddenError, ConflictError, UnauthorizedError


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
            raise ConflictError("Нікнейм вже зайнятий")

    @staticmethod
    async def check_user(
            session: AsyncSession,
            nickname: str,
            password: str,
    ):
        result = await AuthRepository.check(session,nickname)

        if not result or not bcrypt.checkpw(password.encode('utf-8'), result.password.encode('utf-8')):
            raise UnauthorizedError("Неправильний логін та/або пароль")

        if result.is_banned:
            raise ForbiddenError("Доступ заблоковано")

        payload = {
                "sub": result.nickname,
                "id": result.id,
                "role": result.role,
                "exp": datetime.now(timezone.utc) + timedelta(hours=24)
            }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")