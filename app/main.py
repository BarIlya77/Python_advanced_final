import os
from .database import Base, engine, get_db, init_test_data, AsyncSessionLocal
from . import crud, schemas, models
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, status, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from pathlib import Path

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)

app = FastAPI()

static_dir = Path(__file__).resolve().parent.parent / "static"
MEDIA_ROOT = static_dir / "media"


@app.get('/favicon.ico', include_in_schema=False)
async def get_favicon():
    return FileResponse(static_dir / 'favicon.ico')


@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))


app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/js", StaticFiles(directory=os.path.join(static_dir, "js")), name="js")
app.mount("/css", StaticFiles(directory=os.path.join(static_dir, "css")), name="css")

api_router = APIRouter(prefix="/api")


@app.on_event("startup")
async def startup():

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    if os.getenv("ENV") == "development":
        logger.info("Заполнение тестовыми данными")
        async with AsyncSessionLocal() as session:
            await init_test_data(session)

        logger.info("Инициализация БД завершена")
    else:
        logger.info("БД уже инициализирована, пропускаем создание таблиц")


@api_router.get("/users/me", response_model=schemas.UserMeResponse)
async def get_me(api_key: str = Depends(crud.get_api_key), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, api_key=api_key)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.get_user_response(user)


@api_router.post("/tweets", response_model=schemas.CreatedTweet)
async def create_tweet(
        tweet: schemas.TweetCreate,
        api_key: str = Depends(crud.get_api_key),
        db: AsyncSession = Depends(get_db)
):

    user = await crud.get_user(db, api_key=api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    media_items = []
    if tweet.tweet_media_ids:
        media_items = await crud.get_media_by_ids(db, tweet.tweet_media_ids)
    tweet.tweet_media_ids = media_items

    new_tweet = await crud.create_tweet(db, tweet, user.id)

    return {
        "result": True,
        "tweet_id": new_tweet.id
    }


@api_router.post("/medias")
async def upload_media(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):

    file_path = f"static/media/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    db_media = models.Media(url=file_path)
    db.add(db_media)
    await db.commit()
    await db.refresh(db_media)
    return {
        "result": True,
        "media_id": db_media.id
    }


@api_router.get("/tweets", response_model=schemas.TweetResponse)
async def read_tweets(api_key: str = Depends(crud.get_api_key), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, api_key=api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    tweets = await crud.get_tweets(db)
    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found")
    return {
        "result": True,
        "tweets": tweets
    }


@api_router.delete("/tweets/{tweet_id}")
async def delete_tweet(
        tweet_id: int,
        api_key: str = Depends(crud.get_api_key),
        db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, api_key=api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    try:
        tweet = await crud.get_tweet(db, tweet_id=tweet_id)
        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tweet not found"
            )
        if tweet.author_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own tweets"
            )
        if tweet.media:
            for m in tweet.media:
                filename = Path(m.url).name
                media_path = MEDIA_ROOT / filename
                if media_path.exists():
                    media_path.unlink()
                else:
                    logger.info(f'File not found {media_path=}')

        await crud.delete_tweet(db, tweet_id=tweet_id, user_id=user.id)
        return {"result": True}
    except HTTPException as e:
        raise {
            "result": False,
            "error_type": e,
            "error_message": str
        }


@api_router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.get_user_response(db_user)


@api_router.post("/tweets/{tweet_id}/likes")
async def add_like(
        tweet_id: int,
        api_key: str = Depends(crud.get_api_key),
        db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, api_key=api_key)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        await crud.add_like(db, tweet_id=tweet_id, user_id=user.id)
        return {"result": True}

    except HTTPException as e:
        raise {
            "result": False,
            "error_type": e,
            "error_message": str
        }


@api_router.delete("/tweets/{tweet_id}/likes")
async def unlike_tweet(
        tweet_id: int,
        api_key: str = Depends(crud.get_api_key),
        db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, api_key=api_key)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        await crud.remove_like(db, tweet_id=tweet_id, user_id=user.id)
        return {"result": True}

    except HTTPException as e:
        raise {
            "result": False,
            "error_type": e,
            "error_message": str
        }


@api_router.post("/users/{followed_id}/follow")
async def follow_user(
        followed_id: int,
        api_key: str = Depends(crud.get_api_key),
        db: AsyncSession = Depends(get_db)
):
    follower = await crud.get_user(db, api_key=api_key)
    if not follower:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        await crud.add_follower(db, follower_id=follower.id, followed_id=followed_id)
        return {"result": True}

    except HTTPException as e:
        raise {
            "result": False,
            "error_type": e,
            "error_message": str
        }


@api_router.delete("/users/{followed_id}/follow")
async def unfollow(
        followed_id: int,
        api_key: str = Depends(crud.get_api_key),
        db: AsyncSession = Depends(get_db)
):
    follower = await crud.get_user(db, api_key=api_key)

    if not follower:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        await crud.remove_follower(db, follower_id=follower.id, followed_id=followed_id)
        return {"result": True}

    except HTTPException as e:
        raise {
            "result": False,
            "error_type": e,
            "error_message": str
        }


app.include_router(api_router)
