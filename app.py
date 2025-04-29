import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import MODEL_PATH, CHROMA_DIR
from src.models.db import init_db
from src.services.rag import get_rag_chain

# Carga variables de entorno
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: inicializa la base de datos y el pipeline RAG
@app.on_event("startup")
def on_startup():
    init_db()
    # get_rag_chain ya lee MODEL_PATH y CHROMA_DIR internamente
    app.state.rag_chain = get_rag_chain()

# Routers
from src.routers.health import router as health_router
from src.routers.chat import router as chat_router
from src.routers.auth import router as auth_router

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

