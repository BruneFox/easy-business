async def test_user(client, make_user,make_admin):
    admin = await make_admin("admin1")
    for i in range(4):
        await make_user(f"user{i}")
    check_response = await client.get("/api/users",headers=admin)
    assert check_response.status_code == 200
    body = check_response.json()
    assert len(body) == 5
    nicknames = {u["nickname"] for u in body}
    assert nicknames == {"admin1", "user0", "user1", "user2", "user3"}
    assert all("password" not in u for u in body)

async def test_ban_user(client,make_user,make_admin,get_user_id):
    admin = await make_admin("admin2")
    user = await make_user("user1")
    player_id = await get_user_id(admin,"user1")

    response = await client.post(f"/api/users/{player_id}/ban", headers=admin)
    assert response.status_code == 200
    assert "Заблоковано" in response.json()["message"]

    locked = await client.get("/api/businesses", headers=user)
    assert locked.status_code == 403

    response2 = await client.post(f"/api/users/{player_id}/ban", headers=admin)
    assert response2.status_code == 200
    assert "Розблоковано" in response2.json()["message"]

    locked2 = await client.get("/api/businesses", headers=user)
    assert locked2.status_code == 200



async def test_user_ban_user(client,make_user,make_admin,get_user_id):
    admin = await make_admin("admin2")
    user = await make_user("user1")
    player_id = await get_user_id(admin,"user1")

    locked = await client.post(f"/api/users/{player_id}/ban", headers=user)
    assert locked.status_code == 403

async def test_change_money(client, make_user, make_admin, get_user_id):
    admin = await make_admin("admin")
    user = await make_user("user")
    player_id = await get_user_id(admin, "user")

    before = (await client.get("/api/businesses", headers=user)).json()["money"]

    response = await client.post(f"/api/users/{player_id}/balance-adjustments", json={"cash": 100}, headers=admin)
    assert response.status_code == 200

    after = (await client.get("/api/businesses", headers=user)).json()["money"]
    assert after == before + 100



async def test_change_money_for_none(client,make_user,make_admin,get_user_id):
    admin = await make_admin("admin")
    adm_resp = await client.post("/api/users/999/balance-adjustments",headers=admin, json={"cash": 100})
    assert adm_resp.status_code == 404
    assert "Користувача з таким id не існує" in adm_resp.json()["detail"]

async def test_user_cant_change_money(client,make_user,make_admin,get_user_id):
    admin = await make_admin("admin")
    user = await make_user("user")
    admin_id = await get_user_id(admin,"admin")
    player_id = await get_user_id(admin, "user")


    us_resp1 = await client.post(f"/api/users/{player_id}/balance-adjustments",headers=user, json={"cash": 100})
    assert us_resp1.status_code == 403
    us_resp2 = await client.post(f"/api/users/{admin_id}/balance-adjustments", headers=user, json={"cash": 100})
    assert us_resp2.status_code == 403


async def test_give_admin(client,make_user,make_admin,get_user_id):
    admin = await make_admin("admin")
    user = await make_user("user")
    player_id = await get_user_id(admin, "user")

    response = await client.post(f'/api/users/{player_id}/role',headers=admin)
    assert response.status_code == 200
    response_user = await client.get("/api/users",headers=user)
    assert response_user.status_code == 200

async def test_user_dont_give_admin(client,make_user,make_admin,get_user_id):
    admin = await make_admin("admin")
    user = await make_user("user")
    player_id = await get_user_id(admin, "user")

    response = await client.post(f'/api/users/{player_id}/role',headers=user)
    assert response.status_code == 403
    response_user = await client.get("/api/users",headers=user)
    assert response_user.status_code == 403