import pytest
from sqlalchemy import update
from model import User, Busisness


async def test_create_business_success(client, make_user):
    token = await make_user("bruno")

    create_response = await client.post("/create_business",
                json={"name": "test_name_business"},
                headers=token)
    assert create_response.status_code == 200
    body = create_response.json()
    assert body["message"] == "Бізнес успішно створено!"

async def test_check_businesses(client, make_user,create_bus):
    token = await make_user("bruno1")

    for i in range(3):
        await create_bus(token)

    check_response = await client.get("/api/my-business",headers=token)
    assert check_response.status_code == 200
    body = check_response.json()
    assert len(body["busisness"]) == 3

async def test_sell_product(client, db_session, make_user,create_bus):
    from sqlalchemy import update
    from model import Busisness

    token = await make_user("bruno2")
    await create_bus(token)
    check_response = await client.get("/api/my-business",headers=token)
    assert check_response.status_code == 200

    answer = check_response.json()
    money = answer["money"]
    b = answer["busisness"]
    id_b = b[0]["id"]
    lvl_b = b[0]["lvl"]

    await db_session.execute(
        update(Busisness)
        .where(Busisness.id == id_b)
        .values(product=100)
    )
    await db_session.commit()
    sell_response = await client.post(
        "/sell_product",
        json={"id": id_b},
        headers=token
    )
    assert sell_response.status_code == 200

    check_response2 = await client.get("/api/my-business", headers=token)
    assert check_response2.status_code == 200
    answer2 = check_response2.json()
    money2 = answer2["money"]

    assert money2 == money+100*2*int(lvl_b * 1.2)

async def test_upgrate(client,make_user,create_bus):
    token = await make_user("bruno3")
    await create_bus(token)
    check_response = await client.get("/api/my-business", headers=token)
    assert check_response.status_code == 200

    answer = check_response.json()
    money = answer["money"]
    b = answer["busisness"]
    id_b = b[0]["id"]
    lvl_b = b[0]["lvl"]

    upgrate_response = await client.post(
        "/upgrade_business",
        json={"id": id_b},
        headers=token
    )
    assert upgrate_response.status_code == 200
    body = upgrate_response.json()
    assert body["message"] == "Бізнес покращено"

    check_response2 = await client.get("/api/my-business", headers=token)
    assert check_response2.status_code == 200
    answer2 = check_response2.json()
    money2 = answer2["money"]
    b2 = answer2["busisness"]
    lvl_b2 = b2[0]["lvl"]
    assert money2 == money - int(1200*0.75*lvl_b)
    assert lvl_b+1 == lvl_b2



async def test_buy_supplie(client, make_user, create_bus):
    token = await make_user("bruno3")
    await create_bus(token)

    before = (await client.get("/api/my-business", headers=token)).json()
    money = before["money"]
    biz = before["busisness"][0]

    capacity = int(100 * biz["lvl"] * 1.5)
    cost = capacity - biz["warehouse"]

    response = await client.post("/buy_supplie", json={"id": biz["id"]}, headers=token)
    assert response.status_code == 200

    after = (await client.get("/api/my-business", headers=token)).json()
    assert after["busisness"][0]["warehouse"] == capacity
    assert after["money"] == money - cost

@pytest.mark.parametrize("start_money, start_lvl, expected_error", [
    pytest.param(0, 1, "Недостатньо коштів", id="no_money"),
    pytest.param(899, 1, "Недостатньо коштів", id="one_coin_short"),
    pytest.param(1_000_000, 15, "Максимальний рівень бізнесу", id="max_level_rich_user"),
])
async def test_upgrade_rejected(client, make_user, create_bus, db_session,
                                start_money, start_lvl, expected_error):
    headers = await make_user("bruno")
    await create_bus(headers)
    business_id = (await client.get("/api/my-business", headers=headers)).json()["busisness"][0]["id"]

    await db_session.execute(update(User).where(User.nickname == "bruno").values(money=start_money))
    await db_session.execute(update(Busisness).where(Busisness.id == business_id).values(lvl=start_lvl))
    await db_session.commit()

    response = await client.post("/upgrade_business", json={"id": business_id}, headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == expected_error

    after = (await client.get("/api/my-business", headers=headers)).json()
    assert after["money"] == start_money
    assert after["busisness"][0]["lvl"] == start_lvl

@pytest.mark.parametrize("route", ["/upgrade_business", "/buy_supplie", "/sell_product"])
async def test_cannot_touch_foreign_business(client, make_user, create_bus, route):
    alice = await make_user("alice")
    bob = await make_user("bob")
    await create_bus(alice)

    alice_data = (await client.get("/api/my-business", headers=alice)).json()
    alice_business = alice_data["busisness"][0]

    response = await client.post(route, json={"id": alice_business["id"]}, headers=bob)

    assert response.status_code == 400

    alice_after = (await client.get("/api/my-business", headers=alice)).json()
    assert alice_after["busisness"][0] == alice_business
    assert alice_after["money"] == alice_data["money"]