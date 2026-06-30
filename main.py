# app/main.py
from fastapi import FastAPI

from apps import setup_routers
from apps.posts.models import Comment, Like, Post  # noqa
from apps.users.models import User  # noqa

app = FastAPI(
    title="Medical Task API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


setup_routers(app)
