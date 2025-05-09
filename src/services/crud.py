from sqlmodel import Session, select
from src.models.db import init_db
from src.models.schemas import User, Conversation, Message

engine = init_db()

def create_user(email: str, hashed_password: str) -> User:
    with Session(engine) as sess:
        user = User(email=email, hashed_password=hashed_password)
        sess.add(user)
        sess.commit()
        sess.refresh(user)
        return user


def get_user_by_email(email: str) -> User | None:
    with Session(engine) as sess:
        return sess.exec(
            select(User).where(User.email == email)
        ).first()


def create_conversation(user_id: int) -> Conversation:
    with Session(engine) as sess:
        conv = Conversation(user_id=user_id)
        sess.add(conv)
        sess.commit()
        sess.refresh(conv)
        return conv


def save_message(conversation_id: int, sender: str, text: str) -> Message:
    with Session(engine) as sess:
        msg = Message(conversation_id=conversation_id, sender=sender, text=text)
        sess.add(msg)
        sess.commit()
        sess.refresh(msg)
        return msg

# --- Nuevas funciones CRUD ---

def get_conversations_by_user(user_id: int) -> list[Conversation]:
    """
    Retorna todas las conversaciones (sin mensajes) pertenecientes al usuario.
    """
    with Session(engine) as sess:
        return sess.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        ).all()


def get_messages_by_conversation(user_id: int, conversation_id: int) -> list[Message]:
    """
    Retorna todos los mensajes de una conversación si pertenece al usuario,
    de lo contrario retorna lista vacía.
    """
    with Session(engine) as sess:
        conv = sess.get(Conversation, conversation_id)
        if not conv or conv.user_id != user_id:
            return []
        return sess.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
        ).all()
