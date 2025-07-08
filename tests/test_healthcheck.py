import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient):
    assert isinstance(async_client, AsyncClient)  # Должно быть True
    response = await async_client.get("/")
    assert response.status_code == 200
