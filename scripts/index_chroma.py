import glob
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from src.core.config import CHROMA_DIR, MODEL_PATH


def main():
    # Extrae el nombre de modelo para Ollama (sin el prefijo "ollama://")
    model_name = MODEL_PATH.split("//")[-1]

    # 0) Asegúrate de haber descargado el modelo localmente:
    #    ejecuta en tu terminal: ollama pull " + model_name + "

    # 1) Configurar embeddings y vectorstore
    embeddings = OllamaEmbeddings(model=model_name)
    db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="default"
    )

    # 2) Preparar el text splitter
    splitter = CharacterTextSplitter(
        chunk_size=1000,      # tamaño máximo de caracteres por chunk
        chunk_overlap=200     # solapamiento entre chunks
    )

    # 3) Cargar documentos .txt y .pdf desde data/
    txt_paths = glob.glob("data/*.txt")
    pdf_paths = glob.glob("data/*.pdf")
    loaders = [TextLoader(p, encoding="utf8") for p in txt_paths] + [PyPDFLoader(p) for p in pdf_paths]

    # 4) Leer y dividir todos los documentos
    all_chunks = []
    for loader in loaders:
        docs = loader.load()  # lista de Document
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)

    print(f"Archivos TXT encontrados: {len(txt_paths)}")
    print(f"Archivos PDF encontrados: {len(pdf_paths)}")
    print(f"Total de chunks generados: {len(all_chunks)}")

    # 5) Indexar y persistir en Chroma
    db.add_documents(all_chunks)
    # Con Chroma >=0.4.x los datos se persisten automáticamente al usar persist_directory
    # (no existe el método persist()).
    print(f"✅ Indexado completo: {len(all_chunks)} chunks en '{CHROMA_DIR}' usando modelo '{model_name}'")


if __name__ == "__main__":
    main()