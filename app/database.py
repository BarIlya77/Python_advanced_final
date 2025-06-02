from . import models
import os
import random
from datetime import datetime, timezone

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')


DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


fake = Faker()


async def init_test_data(db: AsyncSession):
    if await db.scalar(select(models.User).limit(1)):
        return

    users = [
        models.User(
            name=fake.name(),
            # api_key=fake.uuid4(),
            api_key='test' + (str(i) if i > 0 else ''),
            tweets=[
                models.Tweet(tweet_data=fake.sentence(),
                             created_at=datetime.now(timezone.utc))
                for _ in range(3)
            ]
        )
        for i in range(10)
    ]

    db.add_all(users)
    await db.commit()

    for user in users:
        to_follow = random.sample(users, min(3, len(users)))
        db.add_all([
            models.Follow(follower_id=user.id, followed_id=target.id)
            for target in to_follow if target.id != user.id
        ])

    await db.commit()
