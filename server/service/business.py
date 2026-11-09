from datetime import datetime,timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from repository.business import BusinessRepository
from exceptions import AppError, NotFoundError, ForbiddenError

def math_business(business_obj):
    now = datetime.now()
    delta = int((now - business_obj.last_update).total_seconds())

    warehouse_per_tick = 10 * business_obj.lvl
    product_per_tick = 5 * business_obj.lvl

    tick_by_time = delta // 60

    if tick_by_time <= 0:
        return
    max_capacity = 100 * business_obj.lvl

    tick_by_warh = business_obj.warehouse // warehouse_per_tick
    tick_by_prod = (max_capacity-business_obj.product)//product_per_tick

    actual_ticks = min(tick_by_time, tick_by_prod, tick_by_warh)

    if actual_ticks <= 0:
        business_obj.last_update = now
        return

    business_obj.warehouse -= actual_ticks*warehouse_per_tick
    business_obj.product += actual_ticks*product_per_tick
    business_obj.last_update += timedelta(seconds=actual_ticks * 60)


class BusinessService:
    @staticmethod
    async def buy_new_business(
            session: AsyncSession,
            bis_data: str,
            user_id: int,
    ):
        price = 500
        user = await BusinessRepository.search_user(session,user_id)
        if not user:
            raise NotFoundError("користувача не знайдено")
        if user.money < price:
            raise AppError("Недостатньо коштів")
        user.money -=price
        new_business = await BusinessRepository.create(session, bis_data,user_id)
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
        user_and_business = await BusinessRepository.search_business(session,bis_id,id)
        if not user_and_business:
            raise NotFoundError("Бізнес не знайдено")
        user_obj = user_and_business[0]
        business_obj = user_and_business[1]
        math_business(business_obj)
        amount_to_buy = int(100 * business_obj.lvl * 1.5) - business_obj.warehouse
        if amount_to_buy <= 0:
            raise AppError("Склад заповнений")
        cost = amount_to_buy * 1
        if user_obj.money < cost:
            raise AppError("Недостатньо коштів")
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
            raise NotFoundError("Бізнес не знайдено")
        user_obj = user_and_business[0]
        business_obj = user_and_business[1]

        math_business(business_obj)

        if business_obj.product <= 0:
            raise AppError("Немає товару для продажу")
        price = business_obj.product*2 * int(business_obj.lvl * 1.2)
        user_obj.money += price
        business_obj.product = 0

        await session.commit()
        return user_obj, business_obj

    @staticmethod
    async def upgrade(
            session: AsyncSession,
            bis_id,
            id: int
    ):
        upgradet_business = await BusinessRepository.search_business(session,bis_id,id)
        if not upgradet_business:
            raise NotFoundError("Бізнес не знайдено")

        user_up = upgradet_business[0]
        business_up = upgradet_business[1]

        if business_up.lvl == 15:
            raise AppError("Максимальний рівень бізнесу")
        upgrate_price = int(1200*0.75*business_up.lvl)

        if user_up.money>=upgrate_price:
            user_up.money -= upgrate_price
            business_up.lvl += 1
            await session.commit()
            return user_up, business_up
        else:
            raise AppError("Недостатньо коштів")