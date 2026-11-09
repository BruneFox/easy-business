from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_current_user, get_db
from schemas import BusinessData
from service.business import BusinessService

router = APIRouter(prefix="/api/businesses", tags=["businesses"])

@router.post("",status_code=201)
async def create_business(
        bis: BusinessData,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    await BusinessService.buy_new_business(session,bis.name,current_user["id"])
    return {"message": "Бізнес успішно створено!"}


@router.get("")
async def get_my_business(current_user: dict = Depends(get_current_user),
                          session: AsyncSession = Depends(get_db)
):

    result_arr,money = await BusinessService.watch_user_business(session,current_user["id"])
    return {"message": f" {current_user['nickname']}",
            "money": money,
            "busisness":result_arr}

@router.post("/{business_id}/supplies")
async def buy_supplie(business_id: int,
                      session: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user),
                      ):
    await BusinessService.buysup(session,business_id,current_user["id"])
    return {"message": "Бізнес поповнив склад"}

@router.post("/{business_id}/sales")
async def sell_product(business_id: int,
                      session: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user),
                      ):
    await BusinessService.sell(session,business_id,current_user["id"])
    return {"message": "Товар продано"}

@router.post("/{business_id}/upgrade")
async def upgrade_business(business_id: int,
                      session: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user),
                      ):
    await BusinessService.upgrade(session, business_id, current_user["id"])
    return {"message": "Бізнес покращено"}