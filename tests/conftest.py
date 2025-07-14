import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import delete
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

    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            # await session.execute(delete(Follow))
            # await session.execute(delete(Tweet))
            # await session.execute(delete(User))
            await session.commit()
            yield session
        finally:

            await session.rollback()


@pytest.fixture
async def test_user(db_session):
    from app.models import User

    # await db_session.execute(delete(User).where(User.api_key == "fixed_test_key"))
    # await db_session.commit()

    user = User(name="Fixed_Test_User", api_key="fixed_test_key")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user






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
