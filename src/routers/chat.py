from fastapi import APIRouter, Request
from pydantic import BaseModel
from src.services.crud import create_conversation, save_message
from src.services.rag import get_rag_chain

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    prompt: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    # 1) crea conversación
    conv = create_conversation(req.user_id)
    save_message(conv.id, "user", req.prompt)

    # 2) corre RAG
    chain = request.app.state.rag_chain
    answer = chain.run(req.prompt)

    # 3) guarda respuesta
    save_message(conv.id, "assistant", answer)
    return {"conversation_id": conv.id, "response": answer}
