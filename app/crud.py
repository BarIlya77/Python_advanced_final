from typing import List

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload, selectinload

from . import models, schemas

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tweet(
        db: AsyncSession,
        tweet: schemas.TweetCreate,
        user_id: int,
):

    db_tweet = models.Tweet(
        tweet_data=tweet.tweet_data,
        author_id=user_id,
        media=tweet.tweet_media_ids
    )

    db.add(db_tweet)
    await db.commit()
    await db.refresh(db_tweet)
    return db_tweet


async def get_api_key(api_key: str = Header(..., alias="api-key")) -> str:
    if not api_key:
        raise HTTPException(status_code=403, detail="API key required")
    return api_key


async def get_media_by_ids(
        db: AsyncSession,
        media_ids: List[int],
) -> List[models.Media]:
    if not media_ids:
        return []
    result = await db.execute(
        select(models.Media)
        .where(models.Media.id.in_(media_ids))
    )
    return list(result.scalars().all())


async def delete_tweet(db: AsyncSession, tweet_id: int, user_id: int):
    result = await db.execute(
        delete(models.Tweet)
        .where(
            models.Tweet.id == tweet_id,
            models.Tweet.author_id == user_id
        )
        .returning(models.Tweet.id)
    )
    deleted_id = result.scalar_one_or_none()

    if not deleted_id:
        raise HTTPException(status_code=404, detail="Tweet not found or already removed")

    await db.commit()
    return {"status": "success"}


async def get_tweet(db: AsyncSession, tweet_id: int):
    result = await db.execute(select(models.Tweet).
                              options(selectinload(models.Tweet.media)).
                              where(models.Tweet.id == tweet_id))
    return result.scalars().first()


async def get_tweets(db: AsyncSession):
    result = await db.execute(
        select(models.Tweet).
        options(selectinload(models.Tweet.media),
                selectinload(models.Tweet.author)).
        order_by(models.Tweet.created_at.desc())
    )
    tweets = result.scalars().all()
    result = []
    for tweet in tweets:
        likes_result = await db.execute(
            select(models.Like).
            options(joinedload(models.Like.user)).
            where(models.Like.tweet_id == tweet.id)
        )
        likes = likes_result.scalars().all()
        result.append({
                    "id": tweet.id,
                    "content": tweet.tweet_data,
                    "attachments": [media.url for media in tweet.media] if tweet.media else None,
                    "author": {
                        "id": tweet.author_id,
                        "name": tweet.author.name
                    },
                    "likes": [
                        {
                            "user_id": like.user_id,
                            "name": like.user.name
                        }
                        for like in likes
                    ]
                })

    return result


async def get_user(db: AsyncSession, **filters):
    query = (
        select(models.User)
        .options(
            selectinload(models.User.followers).joinedload(models.Follow.follower),
            selectinload(models.User.following).joinedload(models.Follow.followed)
        )
        .filter_by(**filters)
    )
    result = await db.execute(query)
    return result.scalars().first()


async def add_like(db: AsyncSession, tweet_id: int, user_id: int):
    existing_like = await db.execute(
        select(models.Like).where(
            models.Like.user_id == user_id,
            models.Like.tweet_id == tweet_id
        )
    )
    if existing_like.scalar():
        raise HTTPException(status_code=400, detail="Like already exists")

    new_like = models.Like(user_id=user_id, tweet_id=tweet_id)
    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)
    return {"result": True, "like_id": new_like.id}


async def remove_like(db: AsyncSession, tweet_id: int, user_id: int):
    result = await db.execute(
        select(models.Like).where(
            models.Like.user_id == user_id,
            models.Like.tweet_id == tweet_id
        )
    )

    like_to_remove = result.scalar_one_or_none()
    if not like_to_remove:
        raise HTTPException(status_code=404, detail="Like not found or already removed")

    await db.delete(like_to_remove)
    await db.commit()
    return {"status": "success"}


async def add_follower(db: AsyncSession, follower_id: int, followed_id: int):
    existing_follower = await db.execute(
        select(models.Follow).where(
            models.Follow.follower_id == follower_id,
            models.Follow.followed_id == followed_id,
        )
    )
    if existing_follower.scalar():
        raise HTTPException(status_code=400, detail="Follower already exists")

    new_follower = models.Follow(follower_id=follower_id, followed_id=followed_id)
    db.add(new_follower)
    await db.commit()
    await db.refresh(new_follower)
    return new_follower


async def remove_follower(db: AsyncSession, follower_id: int, followed_id: int):
    result = await db.execute(
        select(models.Follow).where(
            models.Follow.follower_id == follower_id,
            models.Follow.followed_id == followed_id,
        )
    )

    follower_to_remove = result.scalar_one_or_none()
    if not follower_to_remove:
        raise HTTPException(status_code=404, detail="Follower not found or already removed")

    await db.delete(follower_to_remove)
    await db.commit()
    return {"status": "success"}


async def get_user_response(user):
    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [
                {
                    "id": f.follower.id,
                    "name": f.follower.name
                } for f in user.followers
            ],
            "following": [
                {
                    "id": f.followed.id,
                    "name": f.followed.name
                } for f in user.following
            ]
        }
    }
