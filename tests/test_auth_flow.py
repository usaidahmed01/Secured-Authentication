from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_complete_auth_flow(client):
    email = f"user-{uuid4()}@example.com"
    password = "password123"

    register_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    registered_user = register_response.json()

    assert registered_user["email"] == email
    assert registered_user["is_active"] is True
    assert registered_user["is_superuser"] is False
    assert "id" in registered_user
    assert "created_at" in registered_user
    assert "password" not in registered_user
    assert "hashed_password" not in registered_user

    login_response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    login_tokens = login_response.json()

    assert login_tokens["token_type"] == "bearer"
    assert "access_token" in login_tokens
    assert "refresh_token" in login_tokens

    access_token = login_tokens["access_token"]
    refresh_token = login_tokens["refresh_token"]

    me_response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert me_response.status_code == 200

    current_user = me_response.json()

    assert current_user["email"] == email
    assert current_user["id"] == registered_user["id"]

    refresh_response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 200

    refreshed_tokens = refresh_response.json()

    assert refreshed_tokens["token_type"] == "bearer"
    assert "access_token" in refreshed_tokens
    assert "refresh_token" in refreshed_tokens
    assert refreshed_tokens["access_token"] != access_token
    assert refreshed_tokens["refresh_token"] != refresh_token

    new_access_token = refreshed_tokens["access_token"]

    new_me_response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {new_access_token}",
        },
    )

    assert new_me_response.status_code == 200
    assert new_me_response.json()["email"] == email

    logout_response = await client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {new_access_token}",
        },
    )

    assert logout_response.status_code == 200
    assert logout_response.json()["detail"] == "Revocation complete"

    revoked_token_response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {new_access_token}",
        },
    )

    assert revoked_token_response.status_code == 401
    assert revoked_token_response.json()["detail"] == "Token has been revoked"


@pytest.mark.asyncio
async def test_duplicate_registration_is_blocked(client):
    email = f"duplicate-{uuid4()}@example.com"
    password = "password123"

    first_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_with_wrong_password_fails(client):
    email = f"wrong-password-{uuid4()}@example.com"

    register_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "wrongpassword",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client):
    email = f"refresh-fail-{uuid4()}@example.com"
    password = "password123"

    register_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    refresh_response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token,
        },
    )

    assert refresh_response.status_code == 401
    assert refresh_response.json()["detail"] == "Invalid refresh token"