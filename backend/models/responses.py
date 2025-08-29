from pydantic import BaseModel
from typing import List, Optional, Any

class ApiResponse(BaseModel):
    status: str
    message: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    hearts: int = 0

class PostResponse(BaseModel):
    id: int
    user_id: int
    target_gender: str
    target_job: str
    target_birth_year: int
    target_height: int
    target_app: str
    comment: str
    created_at: str
    likes_count: int = 0
    user_liked: bool = False
    is_owner: bool = False

class ProfileResponse(ApiResponse):
    user_id: int
    user: UserResponse
    comment_posts: List[PostResponse]
    dating_posts: List[Any]