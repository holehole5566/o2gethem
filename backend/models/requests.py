from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class CommentPostCreate(BaseModel):
    target_gender: str
    target_job: str
    target_birth_year: int
    target_height: int
    target_app: str
    comment: str

class DatingPostCreate(BaseModel):
    title: str
    description: str
    target_gender: str
    target_age_min: int
    target_age_max: int

class MessageSend(BaseModel):
    content: str

class MessageReply(BaseModel):
    reply_content: str