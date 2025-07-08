import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import os

from app.main import app
from app.database import get_db, init_test_data
from app import crud, models


# Фикстура для тестового клиента
# @pytest.fixture
# async def async_client(db_session):
#     async def override_get_db():
#         return db_session
#
#     app.dependency_overrides[get_db] = override_get_db
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
#     app.dependency_overrides.clear()


# Фикстура для тестового пользователя
@pytest.fixture
async def test_user(db_session: AsyncSession):
    user_data = {
        "name": "Test User",
        "api_key": "test_api_key"
    }
    user = models.User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


# Тесты здоровья приложения
@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# Тесты пользователей
@pytest.mark.anyio
async def test_get_me(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["name"] == test_user.name
    assert data["user"]["id"] == test_user.id


@pytest.mark.anyio
async def test_get_me_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/api/users/me")
    assert response.status_code == 401


# Тесты твитов
@pytest.mark.anyio
async def test_create_tweet(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": []}
    response = await async_client.post("/api/tweets", json=tweet_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data


@pytest.mark.anyio
async def test_get_tweets(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    # Сначала создаем твит
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": []}
    await async_client.post("/api/tweets", json=tweet_data, headers=headers)

    # Затем получаем список твитов
    response = await async_client.get("/api/tweets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert len(data["tweets"]) > 0


@pytest.mark.anyio
async def test_delete_tweet(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    # Создаем твит
    tweet_data = {"tweet_data": "Test tweet to delete", "tweet_media_ids": []}
    create_response = await async_client.post("/api/tweets", json=tweet_data, headers=headers)
    tweet_id = create_response.json()["tweet_id"]

    # Удаляем твит
    response = await async_client.delete(f"/api/tweets/{tweet_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True


# Тесты медиа
@pytest.mark.anyio
async def test_upload_media(async_client: AsyncClient, test_user, tmp_path):
    headers = {"api-key": test_user.api_key}
    test_file = tmp_path / "test_image.jpg"
    test_file.write_bytes(b"fake image data")

    with open(test_file, "rb") as f:
        response = await async_client.post(
            "/api/medias",
            files={"file": ("test_image.jpg", f, "image/jpeg")},
            headers=headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "media_id" in data


# Тесты лайков
@pytest.mark.anyio
async def test_like_tweet(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    # Создаем твит
    tweet_data = {"tweet_data": "Test tweet to like", "tweet_media_ids": []}
    create_response = await async_client.post("/api/tweets", json=tweet_data, headers=headers)
    tweet_id = create_response.json()["tweet_id"]

    # Ставим лайк
    response = await async_client.post(f"/api/tweets/{tweet_id}/likes", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True


# Тесты подписок
@pytest.mark.anyio
async def test_follow_user(async_client: AsyncClient, test_user, db_session: AsyncSession):
    # Создаем второго пользователя для подписки
    another_user = models.User(name="Another User", api_key="another_api_key")
    db_session.add(another_user)
    await db_session.commit()

    headers = {"api-key": test_user.api_key}
    response = await async_client.post(f"/api/users/{another_user.id}/follow", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_unfollow_user(async_client: AsyncClient, test_user, db_session: AsyncSession):
    # Создаем второго пользователя и подписываемся
    another_user = models.User(name="Another User", api_key="another_api_key")
    db_session.add(another_user)
    await db_session.commit()

    headers = {"api-key": test_user.api_key}
    await async_client.post(f"/api/users/{another_user.id}/follow", headers=headers)

    # Отписываемся
    response = await async_client.delete(f"/api/users/{another_user.id}/follow", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True