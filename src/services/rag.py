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
    # Definición del generador de embeddings, este se usa por el rag tanto como para las preguntas como los documentos que se le den al RAG
    embeddings = OllamaEmbeddings(
        model=MODEL_PATH,
        base_url=OLLAMA_HOST,
    )

    # Crea la bd persistente de chroma en el disco
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="default"
    )

    # Inicializa el modelo
    llm = OllamaLLM(
        model=MODEL_PATH,
        base_url=OLLAMA_HOST,
    )

    # Genera la respuestsa utilizando los 3 primeros chunks que más parecido semántico tengan con la pregunta
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

    return chain
