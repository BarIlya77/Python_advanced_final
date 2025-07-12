import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, delete
from app.main import app
from app.database import Base, get_db
from app.models import User, Tweet, Follow

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Изолированная сессия для каждого теста"""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            # Очистка перед тестом
            await session.execute(delete(Follow))
            await session.execute(delete(Tweet))
            await session.execute(delete(User))
            await session.commit()
            yield session
        finally:
            # Откат изменений после теста
            await session.rollback()


@pytest.fixture(scope="session")
async def _global_test_user(engine):
    """Приватная фикстура для создания пользователя"""
    async with AsyncSession(engine) as session:
        await session.execute(delete(Follow))
        await session.execute(delete(Tweet))
        await session.execute(delete(User)) #.where(User.api_key.like("global_test_%")))
        await session.commit()

        user = User(name="Test_User", api_key="test_api_key")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
async def test_user(_global_test_user, db_session):
    """Основная фикстура пользователя"""
    # Возвращаем пользователя, созданного в отдельной сессии
    return _global_test_user


@pytest.fixture
async def async_client(db_session):
    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()