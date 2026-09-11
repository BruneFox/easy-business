from datetime import datetime,timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repository.business import BusinessRepository
from schemas import BusinessData


def math_business(business_obj):
    now = datetime.now()
    delta = int((now - business_obj.last_update).total_seconds())

    warehouse_per_tick = 10
    product_per_tick = 5

    tick_by_time = delta // 60

    if tick_by_time <= 0:
        return

    tick_by_warh = business_obj.warehouse // warehouse_per_tick
    tick_by_prod = (100-business_obj.product)//product_per_tick

    actual_ticks = min(tick_by_time, tick_by_prod, tick_by_warh)

    if actual_ticks <= 0:
        business_obj.last_update = now
        return

    business_obj.warehouse -= actual_ticks*warehouse_per_tick
    business_obj.product += actual_ticks*product_per_tick
    business_obj.last_update += timedelta(seconds=actual_ticks* 60)


class BusinessService:
    @staticmethod
    async def buy_new_business(
            session: AsyncSession,
            bis_data: BusinessData,
            user_id: int,
    ):
        price = 500
        user = await BusinessRepository.search_user(session,user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Користувача не знайдено")

        if user.money < price:
            raise HTTPException(status_code=400, detail="Недостатньо коштів!")

        user.money -=price
        new_business = await BusinessRepository.create(session, bis_data.name,user_id)
        await session.commit()
        return new_business

    @staticmethod
    async def watch_user_business(
            session: AsyncSession,
            user_id:int):

        user = await BusinessRepository.search_user(session, user_id)
        business = await BusinessRepository.watch(session, user_id)
        result_arr=[]
        if business:
            for b in business:
                math_business(b)
                result_arr.append({
                    "id": b.id,
                    "lvl": b.lvl,
                    "business_name": b.business_name,
                    "warehouse": b.warehouse,
                    "product": b.product
                })
            await session.commit()

        money = user.money if user else 0
        return business, money

    @staticmethod
    async def buysup(
            session: AsyncSession,
            bis_id,
            id: int):
        price = 100
        user_and_business = await BusinessRepository.search_business(session,bis_id,id)
        if not user_and_business:
            raise HTTPException(status_code=404, detail="Користувача не знайдено")
        user_obj = user_and_business[0]
        business_obj = user_and_business[1]
        if user_obj.money < price:
            raise HTTPException(status_code=400, detail="Недостатньо коштів!")
        math_business(business_obj)
        amount_to_buy = 100 - business_obj.warehouse
        if amount_to_buy <= 0:
            raise HTTPException(status_code=400, detail="Склад вже повністю заповнений!")
        cost = amount_to_buy * 1
        if user_obj.money < cost:
            raise HTTPException(status_code=400, detail="Недостатньо коштів!")
        user_obj.money -= cost
        business_obj.warehouse += amount_to_buy

        await session.commit()
        return user_obj,business_obj

    @staticmethod
    async def sell(
            session: AsyncSession,
            bis_id,
            id: int):
        user_and_business = await BusinessRepository.search_business(session, bis_id, id)

        if not user_and_business:
            raise HTTPException(status_code=404, detail="Користувача не знайдено")

        user_obj = user_and_business[0]
        business_obj = user_and_business[1]

        math_business(business_obj)

        if business_obj.product <= 0:
            raise HTTPException(status_code=400, detail="Немає готового товару для продажу!")

        price = business_obj.product*2
        user_obj.money += price
        business_obj.product = 0

        await session.commit()
        return user_obj, business_obj


