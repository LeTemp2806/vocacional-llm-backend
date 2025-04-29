from langchain_community.llms import LlamaCpp
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from src.core.config import MODEL_PATH, CHROMA_DIR


def get_rag_chain() -> RetrievalQA:
    """
    Crea y devuelve un pipeline RAG:
     - LLaMA cuantizado vía LlamaCpp
     - Chroma como vectorstore
     - RetrievalQA de LangChain uniendo ambos
    """
    # 1) Carga el modelo LLaMA cuantizado
    llm = LlamaCpp(
        model_path=MODEL_PATH,
        n_ctx=1024,
        temperature=0.2,
    )

    # 2) Conecta con Chroma (índice ya poblado)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=llm.get_embedding_function(),
    )

    # 3) Construye el chain RetrievalQA
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=False
    )

    return chain

# src/routers/auth.py
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
