from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from src.services.crud import create_conversation, save_message

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    prompt: str

class SourceItem(BaseModel):
    text: str
    metadata: dict

class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: list[SourceItem]

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    # 1) crea nueva conversación y guarda mensaje del usuario
    conv = create_conversation(req.user_id)
    save_message(conv.id, "user", req.prompt)

    # 2) corre RAG y solicita que devuelva documentos fuente
    chain = request.app.state.rag_chain
    result = chain.invoke(
        {"query": req.prompt},
        return_only_outputs=False
    )

    # 3) extrae la respuesta con la clave correcta y aplica fallback si viene vacío
    answer = result.get("result")
    if not answer:
        # Si prefieres lanzar un error en vez de fallback:
        # raise HTTPException(status_code=500, detail="La LLM devolvió None")
        answer = "Lo siento, no pude generar una respuesta en este momento."

    # 4) guarda respuesta generada
    save_message(conv.id, "assistant", answer)

    # 5) formatea sources para la respuesta
    source_docs = result.get("source_documents", [])
    sources = [
        SourceItem(text=doc.page_content, metadata=doc.metadata or {})
        for doc in source_docs
    ]

    return ChatResponse(
        conversation_id=conv.id,
        answer=answer,
        sources=sources
    )
