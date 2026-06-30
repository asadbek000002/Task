# Stdlib
from datetime import datetime
from typing import List
from uuid import UUID

# Fastapi
from fastapi import APIRouter, Depends, HTTPException, Response

# SQLAlchemy
from sqlalchemy.orm import Session, selectinload

# Project
from apps.comments.schemas import CommentCreate
from apps.posts.models import Comment, Post
from apps.posts.schemas import CommentOut
from apps.users.auth import get_current_user, require_verified_user
from apps.users.models import User
from core.database import get_db

router = APIRouter()


@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
def get_comments(
    post_id: UUID,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )
    comments = (
        db.query(Comment)
        .options(selectinload(Comment.author))
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [
        CommentOut(
            id=c.id,
            content=c.content,
            author_username=c.author.username,
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(
    post_id: UUID,
    data: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_verified_user(user)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        author_id=user.id,
        content=data.content,
        created_at=datetime.utcnow(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentOut(
        id=comment.id,
        content=comment.content,
        author_username=user.username,
        created_at=comment.created_at,
    )


@router.delete("/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_verified_user(user)
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not allowed to delete this comment"
        )
    db.delete(comment)
    db.commit()
    return Response(status_code=204)
