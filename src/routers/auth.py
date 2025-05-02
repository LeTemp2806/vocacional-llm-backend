from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.services.crud import create_user, get_user_by_email
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from src.core.config import SECRET_KEY, ALGORITHM

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
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed = pwd_context.hash(req.password)
    user = create_user(req.email, hashed)
    return RegisterResponse(id=user.id, email=user.email)