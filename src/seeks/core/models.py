from enum import Enum
from typing import List

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seeks.core.database import Base


class Provider(Base):
    __tablename__ = "provider"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    api_key: Mapped[str]
    models: Mapped[List["Model"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name='{self.name}')>"


class Model(Base):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("provider.id"))
    provider: Mapped["Provider"] = relationship(back_populates="models")
    assistants: Mapped[List["Assistant"]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Model(id={self.id}, name='{self.name}')>"


class Assistant(Base):
    __tablename__ = "assistant"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str]
    model_id: Mapped[int] = mapped_column(ForeignKey("model.id"))
    model: Mapped["Model"] = relationship(back_populates="assistants")
    threads: Mapped[List["Thread"]] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Assistant(id={self.id}, name='{self.name}')>"


class Thread(Base):
    __tablename__ = "thread"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistant.id"))
    assistant: Mapped["Assistant"] = relationship(back_populates="threads")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Thread(id={self.id}, name='{self.name}')>"


class RoleType(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[RoleType] = mapped_column(SQLAlchemyEnum(RoleType))
    text: Mapped[str]
    thread_id: Mapped[int] = mapped_column(ForeignKey("thread.id"))
    thread: Mapped["Thread"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role='{self.role}', text='{self.text}')>"
