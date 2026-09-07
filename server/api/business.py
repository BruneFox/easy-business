from http.client import HTTPException
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from dependency import get_current_user, get_db
from schemas import BusinessData
from service.business import BusinessService

router = APIRouter()

@router.post("/create_business")
async def create_business(
        bis: BusinessData,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    try:
        await BusinessService.buy_new_business(session,bis,current_user["id"])
        return {"message": "Бізнес успішно створено!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/my-business")
async def get_my_business(current_user: dict = Depends(get_current_user),
                          session: AsyncSession = Depends(get_db)
):

    result_arr = await BusinessService.watch_user_business(session,current_user["id"])
    return {"message": f" {current_user['nickname']}",
            "money": 5000,
            "busisness":result_arr}

