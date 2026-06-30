from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from apps.users.auth import get_current_user, hash_password, verify_password
from apps.users.models import User
from apps.users.schemas import (
    LoginSchemaIn,
    LoginSchemaOut,
    RegisterSchemaIn,
    RegisterSchemaOut,
    UpdateMeSchemaIn,
    UserSchemaOut,
)
from core.database import get_db

from .auth import create_access_token
from .tasks import send_verification_email_task

router = APIRouter()


@router.post("/register", response_model=RegisterSchemaOut)
def register(data: RegisterSchemaIn, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.email == data.email) | (User.username == data.username))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already exists.")

    hashed_password = hash_password(data.password)
    verification_token = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    new_user = User(
        email=data.email,
        username=data.username.lower(),
        full_name=data.full_name,
        password_hash=hashed_password,
        is_verified=False,
        email_verification_token=verification_token,
        email_verification_expires_at=expires_at,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email_task.delay(new_user.email, verification_token)

    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "is_verified": new_user.is_verified,
    }


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_verification_token == token).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")

    if (
        not user.email_verification_expires_at
        or user.email_verification_expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Verification token expired")

    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_expires_at = None

    db.commit()
    db.refresh(user)

    return {
        "detail": f"Email {user.email} successfully verified",
        "username": user.username,
        "is_verified": user.is_verified,
    }


@router.post("/login", response_model=LoginSchemaOut)
def login(data: LoginSchemaIn, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == data.email).first()
    if not db_user or not verify_password(data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token_data = {"user_id": str(db_user.id)}
    access_token = create_access_token(token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserSchemaOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/users/me")
def update_me(
    data: UpdateMeSchemaIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.full_name is None and data.username is None and data.email is None:
        raise HTTPException(status_code=400, detail="Nothing to update")

    email_changed = False

    if data.username and data.username != current_user.username:
        exists = db.query(User).filter(User.username == data.username).first()
        if exists:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = data.username.lower()

    if data.full_name:
        current_user.full_name = data.full_name

    if data.email and data.email != current_user.email:
        exists = db.query(User).filter(User.email == data.email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already in use")

        token = str(uuid4())

        current_user.email = data.email
        current_user.is_verified = False
        current_user.email_verification_token = token
        current_user.email_verification_expires_at = datetime.now(
            timezone.utc
        ) + timedelta(hours=24)

        email_changed = True

    db.commit()
    db.refresh(current_user)

    if email_changed:
        send_verification_email_task.delay(
            current_user.email, current_user.email_verification_token
        )

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_verified": current_user.is_verified,
        "email_verification_required": email_changed,
    }
