from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_session
from model import async_session_maker, User, engine, Base
import hashlib
from pathlib import Path
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserData(BaseModel):
    nickname: str
    email: str
    password: str

class UserLogin(BaseModel):
    nickname: str
    password: str

BASE_DIR = Path(__file__).resolve().parent.parent
@app.get("/")
async def start_page():
    file_path = BASE_DIR / "client" / "register.html"
    return FileResponse(file_path)

@app.post("/register")
async def register_page(user: UserData):
    async with (async_session_maker() as session):
        try:
            pasw_bytes = bcrypt.hashpw(user.password.encode('utf-8'),bcrypt.gensalt())
            pasw_str = pasw_bytes.decode('utf-8')
            user_db = User(nickname = user.nickname, email = user.email, password = pasw_str)

            session.add(user_db)

            await session.commit()

            return {"message": "Користувач зареєструвався!", "nickname": user.nickname}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
async def login_page(check_user: UserLogin):
    async with (async_session_maker() as session):
        try:
            check_name = select(User).where(User.nickname == check_user.nickname)
            name_session = await session.execute(check_name)
            result_name = name_session.scalar_one_or_none()
            if result_name:
                check_paswus =check_user.password.encode('utf-8')
                check_paswdb = result_name.password.encode('utf-8')
                if bcrypt.checkpw(check_paswus, check_paswdb):
                    SECRET_KEY = "my_super_secret_business_key"
                    payload = {
                        "sub": result_name.nickname,
                        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
                    }
                    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                    return {"message": "Користувач війшов", "access_token": token}
            raise HTTPException(status_code=401, detail="неправильний логін та/або пароль")
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Помилка сервера: {e}")





@app.get("/players")
async def serve_users_page():
    file_path = BASE_DIR / "client" / "users.html"
    return FileResponse(file_path)

@app.get("/users")
async def get_user():
    async with async_session_maker() as session:
        s = await session.execute(select(User))
        result = s.scalars().all()
        return result