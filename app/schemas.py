from fastapi import UploadFile
from pydantic import BaseModel
from typing import List, Optional


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class CreatedTweet(BaseModel):
    result: bool
    tweet_id: int


class MediaCreate(BaseModel):
    file: UploadFile


class UserBase(BaseModel):
    id: int
    name: str


class FollowerInfo(BaseModel):
    id: int
    name: str


class UserById(UserBase):
    followers: list[FollowerInfo]
    following: list[FollowerInfo]


class UserMeResponse(BaseModel):
    result: bool
    user: UserById


class LikeSchema(BaseModel):
    user_id: int
    name: str


class TweetSchema(BaseModel):
    id: int
    content: str
    attachments: Optional[List[str]]
    author: 'UserBase'
    likes: List['LikeSchema']


class TweetResponse(BaseModel):
    result: bool
    tweets: list['TweetSchema']
