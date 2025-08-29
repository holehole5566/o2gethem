from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.user_service import UserService
from services.session_service import SessionService
from services.post_service import PostService
from services.dating_service import DatingService
import uvicorn

import os

DATABASE_DSN = os.getenv("DATABASE_DSN", "postgresql://user:password@localhost:5432/database")

origins = [   
    "http://localhost:5173",
    "https://localhost:5173",   
    "http://127.0.0.1:5173",
    "https://127.0.0.1:5173"
    ]

app = FastAPI()
user_service = UserService(DATABASE_DSN)
post_service = PostService(DATABASE_DSN)
dating_service = DatingService(DATABASE_DSN)
session_service = SessionService(redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"), expire_minutes=int(os.getenv("SESSION_EXPIRE_MINUTES", "30")))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = await session_service.get_user_id(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return user_id

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    try:
        user = user_service.create_user(username, email, password)
        return {"status": "ok", "message": "User created successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login")
async def login(response: Response, request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    user = user_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = await session_service.create_session(user_id=user["id"])
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # 上線改 True
        samesite="lax",
        max_age=1440*60
    )
    return {"message": "Login successful","status":"ok"}

@app.post("/logout")
async def logout(response: Response, request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        await session_service.delete_session(session_id)
    response.delete_cookie("session_id")
    return {"message": "Logged out"}

@app.get("/profile")
async def profile(user_id: int = Depends(get_current_user)):
    try:
        user = user_service.get_user_by_id(user_id)
        user_posts = post_service.get_user_posts(user_id)
        user_dating_posts = dating_service.get_user_dating_posts(user_id)
        return {
            "user_id": user_id, 
            "user": user,
            "comment_posts": user_posts,
            "dating_posts": user_dating_posts,
            "status": "ok"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get profile")

@app.post("/comment_posts")
async def create_comment_post(request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        post = post_service.create_post(
            user_id=user_id,
            target_gender=data.get("target_gender"),
            target_job=data.get("target_job"),
            target_birth_year=data.get("target_birth_year"),
            target_height=data.get("target_height"),
            target_app=data.get("target_app"),
            comment=data.get("comment")
        )
        return {"status": "ok", "post": post}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create comment post")

@app.get("/comment_posts")
async def get_comment_posts(request: Request, user_id: int = None):
    try:
        user_id = request.cookies.get("session_id")
        if user_id:
            user_id = await session_service.get_user_id(user_id)
    except:
        user_id = None
    
    filters = dict(request.query_params)
    try:
        posts = post_service.get_posts(filters if filters else None, user_id)
        return {"status": "ok", "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get comment posts")

@app.put("/comment_posts/{post_id}")
async def update_comment_post(post_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        post = post_service.update_post(
            post_id=post_id,
            user_id=user_id,
            target_gender=data.get("target_gender"),
            target_job=data.get("target_job"),
            target_birth_year=data.get("target_birth_year"),
            target_height=data.get("target_height"),
            target_app=data.get("target_app"),
            comment=data.get("comment")
        )
        if not post:
            raise HTTPException(status_code=404, detail="Comment post not found or not authorized")
        return {"status": "ok", "post": post}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update comment post")

@app.post("/comment_posts/{post_id}/like")
async def like_comment_post(post_id: int, user_id: int = Depends(get_current_user)):
    try:
        success = post_service.like_post(post_id, user_id)
        return {"status": "ok", "liked": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to like comment post")

@app.delete("/comment_posts/{post_id}/like")
async def unlike_comment_post(post_id: int, user_id: int = Depends(get_current_user)):
    try:
        success = post_service.unlike_post(post_id, user_id)
        return {"status": "ok", "unliked": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to unlike comment post")

@app.post("/dating")
async def create_dating_post(request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        post = dating_service.create_dating_post(
            user_id=user_id,
            title=data.get("title"),
            description=data.get("description"),
            target_gender=data.get("target_gender"),
            target_age_min=data.get("target_age_min"),
            target_age_max=data.get("target_age_max")
        )
        return {"status": "ok", "post": post}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create dating post")

@app.get("/dating")
async def get_dating_posts(request: Request):
    try:
        user_id = request.cookies.get("session_id")
        if user_id:
            user_id = await session_service.get_user_id(user_id)
    except:
        user_id = None
    
    filters = dict(request.query_params)
    try:
        posts = dating_service.get_dating_posts(filters if filters else None, user_id)
        return {"status": "ok", "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dating posts")

@app.post("/dating/{post_id}/message")
async def send_message(post_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        message = dating_service.send_message(
            sender_id=user_id,
            dating_post_id=post_id,
            content=data.get("content")
        )
        return {"status": "ok", "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.get("/messages")
async def get_messages(user_id: int = Depends(get_current_user)):
    try:
        messages = dating_service.get_messages(user_id)
        return {"status": "ok", "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get messages")

@app.post("/messages/{message_id}/reply")
async def reply_message(message_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        message = dating_service.reply_message(
            message_id=message_id,
            user_id=user_id,
            reply_content=data.get("reply_content")
        )
        return {"status": "ok", "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reply message")

@app.put("/messages/{message_id}")
async def update_message(message_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        message = dating_service.update_message(
            message_id=message_id,
            user_id=user_id,
            content=data.get("content")
        )
        return {"status": "ok", "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update message")

@app.get("/dating/can_post")
async def can_post_dating(user_id: int = Depends(get_current_user)):
    try:
        can_post = dating_service.can_post_today(user_id)
        return {"status": "ok", "can_post": can_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to check posting status")

if __name__ == "__main__":
    user_service.init_db()
    post_service.init_db()
    dating_service.init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)