from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class CommentCreate(BaseModel):
    content: str

    @field_validator("content")
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Comment content cannot be empty")
        if len(value) > 2000:
            raise ValueError("Comment content must be at most 2,000 characters")
        return value


class CommentOut(BaseModel):
    id: UUID
    content: str
    author_username: str
    created_at: datetime
