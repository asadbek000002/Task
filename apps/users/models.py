# Stdlib
import uuid

# SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.posts.schemas import FeedUserOut

# Project
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(32), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)

    email_verification_token = Column(String, nullable=True, index=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    # # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    @property
    def feed_data(self) -> "FeedUserOut":
        posts_data = [post.feed_data for post in self.posts]
        return FeedUserOut(username=self.username, posts=posts_data)
