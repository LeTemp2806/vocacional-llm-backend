from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

    conversations: List["Conversation"] = Relationship(back_populates="user")

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    sender: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
