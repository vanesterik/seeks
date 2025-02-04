from enum import Enum
from typing import List

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
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
    settings = relationship("Settings", back_populates="provider")

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name='{self.name}')>"


class Model(Base):
    __tablename__ = "model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    provider: Mapped["Provider"] = relationship(back_populates="models")
    provider_id: Mapped[int] = mapped_column(ForeignKey("provider.id"))
    settings = relationship("Settings", back_populates="model")

    def __repr__(self) -> str:
        return f"<Model(id={self.id}, name='{self.name}')>"


class Assistant(Base):
    __tablename__ = "assistant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str]
    threads: Mapped[List["Thread"]] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )
    settings = relationship("Settings", back_populates="assistant")

    def __repr__(self) -> str:
        return f"<Assistant(id={self.id}, name='{self.name}')>"


class Thread(Base):
    __tablename__ = "thread"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    assistant: Mapped["Assistant"] = relationship(back_populates="threads")
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistant.id"))
    messages: Mapped[List["Message"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )
    settings = relationship("Settings", back_populates="thread")

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
    thread: Mapped["Thread"] = relationship(back_populates="messages")
    thread_id: Mapped[int] = mapped_column(ForeignKey("thread.id"))

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role='{self.role}', text='{self.text}')>"


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("instance_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id = Column(Integer, unique=True, default=1)
    provider = relationship("Provider", back_populates="settings")
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("provider.id"),
        nullable=True,
    )
    model = relationship("Model", back_populates="settings")
    model_id: Mapped[int] = mapped_column(
        ForeignKey("model.id"),
        nullable=True,
    )
    assistant = relationship("Assistant", back_populates="settings")
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("assistant.id"),
        nullable=True,
    )
    thread = relationship("Thread", back_populates="settings")
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("thread.id"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Settings(id={self.id}, provider_id={self.provider_id}, model_id={self.model_id}, assistant_id={self.assistant_id}, thread_id={self.thread_id})>"
