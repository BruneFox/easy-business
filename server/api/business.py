from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_current_user, get_db
from schemas import BusinessData, BusinessAction
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
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")


@router.get("/api/my-business")
async def get_my_business(current_user: dict = Depends(get_current_user),
                          session: AsyncSession = Depends(get_db)
):

    result_arr,money = await BusinessService.watch_user_business(session,current_user["id"])
    return {"message": f" {current_user['nickname']}",
            "money": money,
            "busisness":result_arr}

@router.post("/buy_supplie")
async def buy_supplie(bis: BusinessAction,
                      session: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user),
                      ):
    try:
        await BusinessService.buysup(session,bis.id,current_user["id"])
        return {"message": "Бізнес поповнив склад"}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@router.post("/sell_product")
async def sell_product(bis: BusinessAction,
                      session: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user),
                      ):
    try:
        await BusinessService.sell(session,bis.id,current_user["id"])
        return {"message": "Товар продано"}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@router.post("/upgrade_business")
async def upgrade_business(bis: BusinessAction,
                      session: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user),
                      ):
    try:
        await BusinessService.upgrade(session,bis.id,current_user["id"])
        return {"message": "Бізнес покращено"}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")