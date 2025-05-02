# src/core/config.py
import os
from dotenv import load_dotenv

# Determina la ruta base del proyecto para localizar .env y otros recursos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# Ruta al archivo .env
dotenv_path = os.path.join(BASE_DIR, '.env')
# Carga variables de entorno definiendo override=True para asegurar que .env prevalezca
load_dotenv(dotenv_path, override=True)

# Configuración de la base de datos y RAG
DATABASE_URL = os.getenv('DATABASE_URL')
CHROMA_DIR = os.getenv('CHROMA_DIR')
MODEL_PATH = os.getenv('MODEL_PATH')
OLLAMA_HOST = os.getenv('OLLAMA_HOST')

# Configuración de seguridad JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-to-a-random-secret')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
