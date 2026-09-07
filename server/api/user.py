from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_db
from service.user import UserService

router = APIRouter()


@router.get("/users")
async def get_user(session: AsyncSession = Depends(get_db)):return await UserService.check_users(session)