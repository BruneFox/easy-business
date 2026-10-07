import os
import sys
import pathlib

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

SERVER_DIR = pathlib.Path(__file__).resolve().parent.parent / "server"
sys.path.insert(0, str(SERVER_DIR))

os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-prod")

from main import app
from model import Base
from dependency import get_db

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
        await client.post("/register", json=payload)
        login = await client.post("/login", json={
            "nickname": nickname,
            "password": payload["password"],
        })
        return {"Authorization": f"Bearer {login.json()['access_token']}"}
    return _make

@pytest_asyncio.fixture
async def create_bus(client):
    async def _create(token: str):
        create_response = await client.post("/create_business",
                                            json={"name": "test_name_business"},
                                            headers=token)
        body = create_response.json()
        return body
    return _create