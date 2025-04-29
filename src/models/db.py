from sqlmodel import SQLModel, create_engine
from src.core.config import DATABASE_URL

def init_db():
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    return engine
