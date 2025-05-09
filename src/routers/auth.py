from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.services.crud import create_user, get_user_by_email
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from src.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# — Modelos de petición/respuesta —

class RegisterRequest(BaseModel):
    email: str
    password: str

class RegisterResponse(BaseModel):
    id: int
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# — Utilidad para crear el token —

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# — Endpoints —

@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed = pwd_context.hash(req.password)
    user = create_user(req.email, hashed)
    return RegisterResponse(id=user.id, email=user.email)


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or not pwd_context.verify(req.password, user.hashed_password):
        # Ajusta el atributo según cómo guardes la contraseña en tu modelo
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    # Crea el JWT con el id y el email del usuario
    token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    return LoginResponse(access_token=token)
