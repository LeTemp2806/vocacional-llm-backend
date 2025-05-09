from sqlmodel import SQLModel, create_engine
from src.core.config import DATABASE_URL

#Inicialización de la bd y retorno del engine para ser usado en otros lados
def init_db():
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    return engine
