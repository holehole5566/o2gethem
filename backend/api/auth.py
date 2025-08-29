from fastapi import APIRouter, Response, HTTPException, Request
from services.user_service import UserService
from services.session_service import SessionService
from models.requests import UserRegister, UserLogin
from utils.responses import success_response
from config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize services
user_service = UserService(settings.database_dsn)
session_service = SessionService(redis_url=settings.redis_url, expire_minutes=settings.session_expire_minutes)

@router.post("/register")
async def register(user_data: UserRegister):
    
    try:
        user = user_service.create_user(user_data.username, user_data.email, user_data.password)
        return success_response({"user": user}, "User created successfully")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(response: Response, user_data: UserLogin):
    user = user_service.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = await session_service.create_session(user_id=user["id"])
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Change to True in production
        samesite="lax",
        max_age=1440*60
    )
    return success_response(message="Login successful")

@router.post("/logout")
async def logout(response: Response, request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        await session_service.delete_session(session_id)
    response.delete_cookie("session_id")
    return success_response(message="Logged out")