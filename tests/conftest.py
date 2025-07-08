# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from app.database import Base, AsyncSessionLocal, init_test_data
from app.main import app
from httpx import AsyncClient, ASGITransport
import os


# Фикстура для тестового движка БД
@pytest.fixture(scope="session")
async def engine():
    # Используем отдельную тестовую БД
    test_db_url = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")
    engine = create_async_engine(test_db_url, poolclass=NullPool)

    # Создаем и заполняем тестовую БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очистка после всех тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# Фикстура для тестовой сессии БД
@pytest.fixture
async def db_session(engine):
    async with AsyncSessionLocal(bind=engine) as session:
        await init_test_data(session)
        yield session
        # Откатываем транзакцию после теста
        await session.rollback()


# Фикстура для тестового клиента
# @pytest.fixture
# async def async_client(db_session):
#     # Переопределяем зависимость get_db для использования тестовой сессии
#     app.dependency_overrides[get_db] = lambda: db_session
#
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
#
#     # Очищаем переопределения после теста
#     app.dependency_overrides.clear()


@pytest.fixture
async def async_client():
    # Создаем клиент отдельно от async with
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )
    try:
        yield client
    finally:
        await client.aclose()



# Фикстура для тестового пользователя
@pytest.fixture
async def test_user(db_session: AsyncSession):
    from app import crud, models
    user_data = {
        "name": "Test User",
        "api_key": "test_api_key_123"
    }
    user = models.User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user