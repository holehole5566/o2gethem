from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from services.user_service import UserService
from services.session_service import SessionService
from services.post_service import PostService
from services.dating_service import DatingService
from api import auth, users, posts, dating, messages
from dependencies import get_current_user
from middleware.exception_handler import global_exception_handler, http_exception_handler, validation_exception_handler
import uvicorn

from config import settings

DATABASE_DSN = settings.database_dsn

origins = [   
    "http://localhost:5173",
    "https://localhost:5173",   
    "http://127.0.0.1:5173",
    "https://127.0.0.1:5173"
    ]

app = FastAPI()

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(dating.router)
app.include_router(messages.router)
user_service = UserService(DATABASE_DSN)
post_service = PostService(DATABASE_DSN)
dating_service = DatingService(DATABASE_DSN)
session_service = SessionService(redis_url=settings.redis_url, expire_minutes=settings.session_expire_minutes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

















if __name__ == "__main__":
    user_service.init_db()
    post_service.init_db()
    dating_service.init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)