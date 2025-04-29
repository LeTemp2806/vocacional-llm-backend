import os
from dotenv import load_dotenv

# construye la ruta absoluta al .env en la raíz del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")

# carga el .env
loaded = load_dotenv(DOTENV_PATH)
if not loaded:
    # solo un warning en consola para debug
    print(f"⚠️  no pude cargar {DOTENV_PATH}")

# ahora sí lees las variables
DATABASE_URL = os.getenv("DATABASE_URL")
CHROMA_DIR    = os.getenv("CHROMA_DIR")
MODEL_PATH    = os.getenv("MODEL_PATH")
