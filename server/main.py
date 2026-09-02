from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select
from pydantic import BaseModel
from model import async_session_maker, User, engine, Base,Busisness
from pathlib import Path
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default_fallback_key")

app = FastAPI()

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



class UserData(BaseModel):
    nickname: str
    email: str
    password: str
class BusinessData(BaseModel):
    name:str
class UserLogin(BaseModel):
    nickname: str
    password: str

BASE_DIR = Path(__file__).resolve().parent.parent
@app.get("/")
async def start_page():
    file_path = BASE_DIR / "client" / "register.html"
    return FileResponse(file_path)

@app.get("/profile")
async def profile_page():
    file_path = BASE_DIR / "client" / "profile.html"
    return FileResponse(file_path)


@app.get("/api/my-business")
async def get_my_business(current_user: dict = Depends(get_current_user)):
    async with async_session_maker() as session:
        query = select(Busisness).where(Busisness.id_boss ==current_user["id"])
        result = await session.execute(query)
        user_b = result.scalars().all()
        result_arr = []
        for i in user_b:
            result_arr.append({
                "id": i.id,
                "lvl": i.lvl,
                "business_name": i.business_name,
                "warehouse": i.warehouse,
                "product": i.product
                })

    return {"message": f"Секретные бизнес-данные для {current_user['nickname']}", "money": 5000,"busisness":result_arr}

@app.post("/create_business")
async def create_business(bis: BusinessData, current_user: dict = Depends(get_current_user)):
    async with async_session_maker() as session:
        try:
            busis_db = Busisness(business_name = bis.name, id_boss = current_user["id"])
            session.add(busis_db)
            await session.commit()
            return {"message": "Бізнес успішно створено!"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))


@app.post("/register")
async def register_page(user: UserData):
    async with async_session_maker() as session:
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

                    payload = {
                        "sub": result_name.nickname,
                        "id": result_name.id,
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
@app.get("/login_page")
async def serve_login_page():
    file_path = BASE_DIR / "client" / "login.html"
    return FileResponse(file_path)

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