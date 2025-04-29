# src/routers/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.crud import create_user, get_user_by_email
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    email: str
    password: str

class RegisterResponse(BaseModel):
    id: int
    email: str

@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    if get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(req.password)
    user = create_user(req.email, hashed)
    return RegisterResponse(id=user.id, email=user.email)
