import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app import models


# Add user testing
@pytest.mark.anyio
async def test_get_me(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["name"] == test_user.name
    assert data["user"]["id"] == test_user.id
# =================================================================================


# Tweets testing
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
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": []}
    await async_client.post("/api/tweets", json=tweet_data, headers=headers)

    response = await async_client.get("/api/tweets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert len(data["tweets"]) > 0


@pytest.mark.anyio
async def test_delete_tweet(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    tweet_data = {"tweet_data": "Test tweet to delete", "tweet_media_ids": []}
    create_response = await async_client.post("/api/tweets", json=tweet_data, headers=headers)
    tweet_id = create_response.json()["tweet_id"]

    response = await async_client.delete(f"/api/tweets/{tweet_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True
# =================================================================================


# Media testing
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
# =================================================================================


# Like yesting
@pytest.mark.anyio
async def test_like_tweet(async_client: AsyncClient, test_user):
    headers = {"api-key": test_user.api_key}
    tweet_data = {"tweet_data": "Test tweet to like", "tweet_media_ids": []}
    create_response = await async_client.post("/api/tweets", json=tweet_data, headers=headers)
    tweet_id = create_response.json()["tweet_id"]

    response = await async_client.post(f"/api/tweets/{tweet_id}/likes", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True
# =================================================================================


# Follow testing
@pytest.mark.anyio
async def test_follow_user(async_client: AsyncClient, test_user, db_session: AsyncSession):
    new_user = models.User(name="New User", api_key="new_api_key")
    db_session.add(new_user)
    await db_session.commit()

    headers = {"api-key": test_user.api_key}
    response = await async_client.post(f"/api/users/{new_user.id}/follow", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_unfollow_user(async_client: AsyncClient, test_user, db_session: AsyncSession):
    new_user = models.User(name="New User", api_key="new_api_key")
    db_session.add(new_user)
    await db_session.commit()

    headers = {"api-key": test_user.api_key}
    await async_client.post(f"/api/users/{new_user.id}/follow", headers=headers)

    response = await async_client.delete(f"/api/users/{new_user.id}/follow", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] is True
# =================================================================================