from apps.comments.router import router as comments_router
from apps.posts.router import router as posts_router
from apps.users.router import router as users_router


def setup_routers(app):
    app.include_router(users_router, prefix="/api/v1/auth", tags=["users"])
    app.include_router(posts_router, prefix="/api/v1", tags=["posts"])
    app.include_router(comments_router, prefix="/api/v1", tags=["posts"])
