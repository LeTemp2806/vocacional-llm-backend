# app.py

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.core.config import MODEL_PATH, CHROMA_DIR
from src.models.db import init_db
from src.services.rag import get_rag_chain

# Carga variables de entorno
load_dotenv()

app = FastAPI(
    title="Peñin LLM Backend",
    version="0.1.0",
    description="API para registrar usuarios, conversaciones y mensajes con RAG"
)

# CORS para tu front en http://localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arranque de la base de datos y del pipeline RAG
@app.on_event("startup")
def on_startup():
    init_db()
    app.state.rag_chain = get_rag_chain()

# Importa tus routers
from src.routers.auth import router as auth_router
from src.routers.chat import router as chat_router

# Monta los routers:
# 1) /auth → register, login
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# 2) /conversations → GET list, GET messages, (POST ya no se usa aquí)
app.include_router(chat_router, prefix="/conversations", tags=["conversations"])
# 3) /chat → POST para enviar prompt y recibir respuesta del asistente
app.include_router(chat_router, prefix="/chat", tags=["chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
