# Stdlib
from datetime import datetime
from typing import List, Optional
from uuid import UUID

# Fastapi
from fastapi import APIRouter, Depends, HTTPException, Query, Response

# SQLAlchemy
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

# Project
from apps.posts.models import Comment, Like, Post
from apps.posts.schemas import (
    FeedUserOut,
    PostCreate,
    PostDetailOut,
    PostListOut,
    PostOut,
    PostUpdate,
)
from apps.users.auth import get_current_user, require_verified_user
from apps.users.models import User
from core.database import get_db

router = APIRouter()


@router.post("/posts", response_model=PostOut, status_code=201)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_verified_user(user)

    post = Post(
        title=data.title,
        content=data.content,
        author_id=user.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch("/posts/{post_id}", response_model=PostOut)
def update_post(
    post_id: UUID,
    data: PostUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_verified_user(user)
    if data.title is None and data.content is None:
        raise HTTPException(status_code=400, detail="Nothing to update")
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content

    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_verified_user(user)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(post)
    db.commit()
    return Response(status_code=204)


@router.get("/posts/{post_id}", response_model=PostDetailOut)
def get_post_detail(
    post_id: UUID,
    db: Session = Depends(get_db),
):
    post = (
        db.query(Post)
        .options(
            selectinload(Post.comments).selectinload(Comment.author),
            selectinload(Post.likes),
        )
        .filter(Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )
    return post


@router.get("/posts", response_model=List[PostListOut])
def get_posts_list(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search by title or content"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
):
    query = db.query(Post).options(joinedload(Post.author))
    if search:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%"),
            )
        )
    if date_from:
        query = query.filter(Post.created_at >= date_from)
    if date_to:
        query = query.filter(Post.created_at <= date_to)
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    post_ids = [post.id for post in posts]
    likes_map = {}
    if post_ids:
        likes = (
            db.query(Like.post_id, func.count(Like.user_id).label("count"))
            .filter(Like.post_id.in_(post_ids))
            .group_by(Like.post_id)
            .all()
        )

        likes_map = {post_id: count for post_id, count in likes}

    result = []
    for post in posts:
        result.append(
            PostListOut(
                id=post.id,
                title=post.title,
                content=post.content,
                author_username=post.author.username,
                likes_count=likes_map.get(post.id, 0),
                created_at=post.created_at,
            )
        )
    return result


@router.get("/feed", response_model=List[FeedUserOut])
def get_feed(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    users = (
        db.query(User)
        .options(selectinload(User.posts).selectinload(Post.likes))
        .filter(User.is_verified.is_(True))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [user.feed_data for user in users]


@router.post("/posts/{post_id}/like", status_code=201)
def like_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id == user.id:
        raise HTTPException(status_code=403, detail="Cannot like your own post")

    existing_like = (
        db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
    )
    if existing_like:
        raise HTTPException(status_code=400, detail="You have already liked this post")

    like = Like(post_id=post_id, user_id=user.id, created_at=datetime.utcnow())
    db.add(like)
    db.commit()

    return {"detail": "Post liked successfully"}


@router.delete("/posts/{post_id}/like", status_code=204)
def unlike_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like = (
        db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
    )

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return {}
