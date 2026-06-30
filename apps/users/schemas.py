import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterSchemaIn(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if len(value) < 3 or len(value) > 32:
            raise ValueError("Username must be 3-32 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username must contain only letters, numbers, or _")
        return value

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters")
        return value

    @field_validator("full_name")
    def validate_full_name(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 100:
            raise ValueError("Full_name must be 2-100 characters")
        if not re.match(r"^[A-Za-zА-Яа-яЁё\s\-]+$", value):
            raise ValueError("Full name contains invalid characters")
        return value


class RegisterSchemaOut(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class LoginSchemaIn(BaseModel):
    email: EmailStr
    password: str


class LoginSchemaOut(BaseModel):
    access_token: str
    token_type: str


class UserSchemaOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UpdateMeSchemaIn(BaseModel):
    full_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None

    @field_validator("username")
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) < 3 or len(value) > 32:
            raise ValueError("Username must be 3-32 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username must contain only letters, numbers, or _")
        return value

    @field_validator("full_name")
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) < 2 or len(value) > 100:
            raise ValueError("Full_name must be 2-100 characters")
        if not re.match(r"^[A-Za-zА-Яа-яЁё\s\-]+$", value):
            raise ValueError("Full name contains invalid characters")
        return value
