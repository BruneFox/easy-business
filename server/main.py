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

BASE_DIR = Path(__file__).resolve().parent.parent
@app.get("/")
async def start_page():
    file_path = BASE_DIR / "client" / "register.html"
    return FileResponse(file_path)

@app.post("/register")
async def register_page(user: UserData):
    async with async_session_maker() as session:
        try:
            pasw_bytes = user.password.encode('utf-8')
            hash_pasw = hashlib.sha256(pasw_bytes)
            hex_pasw = hash_pasw.hexdigest()

            user_db = User(nickname = user.nickname, email = user.email, password = hex_pasw)

            session.add(user_db)

            await session.commit()

            return {"message": "User finish register!", "nickname": user.nickname}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))


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