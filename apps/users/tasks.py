import asyncio
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy.orm import Session

from apps.email.service import send_verification_email
from apps.users.models import User
from core.celery import app
from core.database import SessionLocal


@app.task
def send_verification_email_task(to_email: str, token: str):
    asyncio.run(send_verification_email(to_email, token))


@shared_task
def delete_unverified_users():
    """
    Deletes users who are older than 24 hours and have is_verified=False
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        users_to_delete = (
            db.query(User)
            .filter(
                User.is_verified == False,
                User.email_verification_expires_at != None,
                User.email_verification_expires_at < now,
            )
            .all()
        )
        for user in users_to_delete:
            db.delete(user)
        db.commit()
        print(f"Deleted {len(users_to_delete)} unverified users")
    finally:
        db.close()
