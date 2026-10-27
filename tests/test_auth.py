async def test_register_success(client):
    response = await client.post("/register", json={
        "nickname": "bruno",
        "email": "test@example.com",
        "password": "strongpassword123",
    })

    assert response.status_code == 200
    body = response.json()
    assert body["nickname"] == "bruno"
    assert body["message"] == "Користувач зареєструвався!"


async def test_register_does_not_return_password(client):
    response = await client.post("/register", json={
        "nickname": "bruno2",
        "email": "hash@example.com",
        "password": "mypassword",
    })

    assert response.status_code == 200
    assert "password" not in response.json()


async def test_register_duplicate_nickname_returns_400(client):
    payload = {"nickname": "bruno3", "email": "a@example.com", "password": "123456"}

    first = await client.post("/register", json=payload)
    assert first.status_code == 200

    second = await client.post("/register", json={**payload, "email": "b@example.com"})

    assert second.status_code == 400
    assert "зайнятий" in second.json()["detail"]


async def test_register_missing_required_field_returns_422(client):

    response = await client.post("/register", json={
        "nickname": "bruno4",
        "email": "e@example.com",
    })

    assert response.status_code == 422


async def test_register_then_login_works(client):
    payload = {
        "nickname": "bruno5",
        "email": "f@example.com",
        "password": "correct-password-123",
    }

    register_response = await client.post("/register", json=payload)
    assert register_response.status_code == 200

    login_response = await client.post("/login", json={
        "nickname": payload["nickname"],
        "password": payload["password"],
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


async def test_login_with_wrong_password_returns_401(client):
    payload = {
        "nickname": "bruno6",
        "email": "g@example.com",
        "password": "correct-password",
    }
    await client.post("/register", json=payload)

    login_response = await client.post("/login", json={
        "nickname": payload["nickname"],
        "password": "totally-wrong-password",
    })

    assert login_response.status_code == 401


async def test_first_user_is_admin(client,make_user):
    first_user = await make_user("user_1")
    second_user = await make_user("user_2")
    check_response = await client.get("/users", headers=first_user)
    assert check_response.status_code == 200
    check_response = await client.get("/users", headers=second_user)
    assert check_response.status_code == 403