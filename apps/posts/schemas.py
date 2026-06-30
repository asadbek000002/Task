# Stdlib
from datetime import datetime
from typing import List
from uuid import UUID

# Pydantic
from pydantic import BaseModel, field_validator

# Project
from apps.comments.schemas import CommentOut


class PostCreate(BaseModel):
    title: str
    content: str

    @field_validator("title")
    def validate_title(cls, value: str) -> str:
        if len(value) < 5 or len(value) > 255:
            raise ValueError("Title must be 5-255 characters")
        return value

    @field_validator("content")
    def validate_content(cls, value: str) -> str:
        if len(value) > 10000:
            raise ValueError("Content must be at most 10,000 characters")
        return value


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

    @field_validator("title")
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) < 5 or len(value) > 255:
            raise ValueError("Title must be 5-255 characters")
        return value

    @field_validator("content")
    def validate_content(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) > 10000:
            raise ValueError("Content must be at most 10,000 characters")
        return value


class PostOut(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime


class PostDetailOut(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime

    comments_data: List[CommentOut] = []
    likes_count: int


class PostListOut(BaseModel):
    id: UUID
    title: str
    content: str
    author_username: str
    likes_count: int = 0
    created_at: datetime


class FeedPostOut(BaseModel):
    id: UUID
    title: str
    content: str
    likes: List[UUID] = []


class FeedUserOut(BaseModel):
    username: str
    posts: List[FeedPostOut] = []
