import os
import sys
import pathlib


SERVER_DIR = pathlib.Path(__file__).resolve().parent.parent / "server"
sys.path.insert(0, str(SERVER_DIR))

os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-prod-0123456789")

from main import app
from model import Base
from dependency import get_db
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, poolclass=None)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def make_user(client):
    async def _make(nickname: str):
        payload = {
            "nickname": f"{nickname}",
            "email": f"{nickname}@example.com",
            "password": "correct-password-123",
        }
        register = await client.post("/api/auth/register", json=payload)
        assert register.status_code == 201, register.text
        login = await client.post("/api/auth/login", json={
            "nickname": nickname,
            "password": payload["password"],
        })
        assert login.status_code == 200, login.text
        return {"Authorization": f"Bearer {login.json()['access_token']}"}
    return _make

@pytest_asyncio.fixture
async def create_bus(client):
    async def _create(headers: str):
        create_response = await client.post("/api/businesses",
                                            json={"name": "test_name_business"},
                                            headers=headers)
        body = create_response.json()
        return body
    return _create

@pytest_asyncio.fixture
async def make_admin(make_user, db_session):
    from sqlalchemy import update
    from model import User

    async def _make(nickname: str):
        headers = await make_user(nickname)
        await db_session.execute(update(User).where(User.nickname == nickname).values(role="Admin"))
        await db_session.commit()
        return headers
    return _make

@pytest_asyncio.fixture
async def get_user_id(client):
    async def _get(admin_headers, nickname: str):
        users = (await client.get("/api/users", headers=admin_headers)).json()
        return next(u["id"] for u in users if u["nickname"] == nickname)
    return _get