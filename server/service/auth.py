from datetime import timedelta, timezone, datetime
import bcrypt
import jwt
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
        return await AuthRepository.create(session,user.nickname,pasw_str,user.email)

    @staticmethod
    async def check_user(
            session: AsyncSession,
            user: UserLogin,
    ):
        result = await AuthRepository.check(session,user.nickname)
        if result:
            check_paswus = user.password.encode('utf-8')
            check_paswdb = result.password.encode('utf-8')
            if bcrypt.checkpw(check_paswus, check_paswdb):
                payload = {
                    "sub": result.nickname,
                    "id": result.id,
                    "exp": datetime.now(timezone.utc) + timedelta(hours=24)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                return token
        return None