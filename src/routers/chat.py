import logging
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from typing import List, Optional
from src.services.crud import (
    create_conversation,
    save_message,
    get_conversations_by_user,
    get_messages_by_conversation,
)
from src.core.security import get_current_user

# Configuración de logger para este módulo
import logging
# Eleva el nivel de logs de SQLAlchemy para ocultar INFO detallados
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("chat")
logger.setLevel(logging.INFO)

router = APIRouter()

# Modelos de petición/respuesta para chat
class ChatRequest(BaseModel):
    user_id: int
    prompt: str
    conversation_id: Optional[int] = None

class MessageItem(BaseModel):
    id: int
    sender: str
    text: str
    timestamp: str

class ChatResponse(BaseModel):
    conversation_id: int
    messages: List[MessageItem]

# Modelo para resumir conversaciones en el sidebar
class ConversationSummary(BaseModel):
    id: int
    last_message: str
    timestamp: str

# 1) Crear nueva conversación (POST /conversations/)
@router.post("/", response_model=ConversationSummary)
async def create_conversation_endpoint(
    current_user=Depends(get_current_user)
):
    conv = create_conversation(current_user.id)
    return ConversationSummary(
        id=conv.id,
        last_message="(sin mensajes)",
        timestamp=conv.created_at.isoformat()
    )

# 2) Enviar mensaje y obtener todo el historial (POST /conversations/message)
@router.post("/message", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    request: Request
):
    # Log de petición
    logger.info(f"Usuario {req.user_id} preguntó: {req.prompt}")

    # Determinar o crear conversación
    if req.conversation_id:
        conv_id = req.conversation_id
    else:
        conv = create_conversation(req.user_id)
        conv_id = conv.id

    # Persistir mensaje del usuario
    save_message(conv_id, "user", req.prompt)

    # Invocar cadena RAG
    chain = request.app.state.rag_chain
    result = chain.invoke({"query": req.prompt}, return_only_outputs=False)

    # Extraer respuesta y fuentes
    answer = result.get("result") or "Lo siento, no pude generar una respuesta."
    sources = result.get("source_documents", [])

    # Log de respuesta
    logger.info(f"Asistente respondió: {answer}")
    logger.info(f"🔍 RAG ejecutado: recuperé {len(sources)} documento(s)")
    for idx, doc in enumerate(sources, start=1):
        snippet = doc.page_content.strip().replace("\n", " ")[:200]
        source_name = doc.metadata.get("source", "desconocido")
        logger.info(
            f"  Fuente {idx}: {source_name} | snippet: «{snippet}...»"
        )

    # Persistir respuesta
    save_message(conv_id, "assistant", answer)

    # Leer todos los mensajes de la conversación
    msgs = get_messages_by_conversation(req.user_id, conv_id)
    items = [MessageItem(
        id=m.id,
        sender=m.sender,
        text=m.text,
        timestamp=m.timestamp.isoformat()
    ) for m in msgs]
    return ChatResponse(conversation_id=conv_id, messages=items)

# 3) Listar conversaciones del usuario autenticado (GET /conversations/)
@router.get("/", response_model=List[ConversationSummary])
async def list_conversations(
    current_user=Depends(get_current_user)
):
    convs = get_conversations_by_user(current_user.id)
    summaries: List[ConversationSummary] = []
    for c in convs:
        msgs = get_messages_by_conversation(current_user.id, c.id)
        if msgs:
            last = msgs[-1]
            summaries.append(ConversationSummary(
                id=c.id,
                last_message=last.text,
                timestamp=last.timestamp.isoformat()
            ))
        else:
            summaries.append(ConversationSummary(
                id=c.id,
                last_message="(sin mensajes)",
                timestamp=c.created_at.isoformat()
            ))
    return summaries

# 4) Obtener mensajes de una conversación específica (GET /conversations/{id}/messages)
@router.get("/{conversation_id}/messages", response_model=List[MessageItem])
async def get_messages(
    conversation_id: int,
    current_user=Depends(get_current_user)
):
    msgs = get_messages_by_conversation(current_user.id, conversation_id)
    return [MessageItem(
        id=m.id,
        sender=m.sender,
        text=m.text,
        timestamp=m.timestamp.isoformat()
    ) for m in msgs]
