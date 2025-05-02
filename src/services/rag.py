# src/services/rag.py
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from src.core.config import MODEL_PATH, CHROMA_DIR, OLLAMA_HOST


def get_rag_chain() -> RetrievalQA:
    """
    Crea y devuelve un pipeline RAG:
     - LLM servido por OllamaLLM
     - Embeddings vía OllamaEmbeddings
     - Vectorstore Chroma desde langchain_chroma
    """
    # 1) Generador de embeddings
    embeddings = OllamaEmbeddings(
        model=MODEL_PATH,
        base_url=OLLAMA_HOST,
    )

    # 2) Conecta con Chroma (índice persistente en disco)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="default"
    )

    # 3) Inicializa el LLM
    llm = OllamaLLM(
        model=MODEL_PATH,
        base_url=OLLAMA_HOST,
    )

    # 4) Construye el chain RetrievalQA
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

    return chain
