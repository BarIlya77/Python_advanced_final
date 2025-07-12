import pytest
from httpx import AsyncClient
from .conftest import db_session


@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_user_creation(db_session):
    from app.models import User
    user = User(name="Test", api_key="test_API_123")
    db_session.add(user)
    await db_session.commit()

    assert user.id is not None
