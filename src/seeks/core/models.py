from enum import Enum
from typing import List

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Provider(Base):
    __tablename__ = "provider"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    api_key: Mapped[str]

    def __repr__(self) -> str:
        return "<Provider(id={}, name={}, api_key={})>".format(
            self.id,
            self.name,
            self.api_key,
        )


class Assistant(Base):
    __tablename__ = "assistant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str]
    model: Mapped[str]
    threads: Mapped[List["Thread"]] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )
    settings = relationship("Settings", back_populates="assistant")

    def __repr__(self) -> str:
        return "<Assistant(id={}, name={}, model={}, description={})>".format(
            self.id,
            self.name,
            self.model,
            self.description,
        )


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
        return "<Thread(id={}, name={})>".format(
            self.id,
            self.name,
        )


class RoleType(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[RoleType] = mapped_column(SQLAlchemyEnum(RoleType))
    content: Mapped[str]
    thread: Mapped["Thread"] = relationship(back_populates="messages")
    thread_id: Mapped[int] = mapped_column(ForeignKey("thread.id"))

    def __repr__(self) -> str:
        return "<Message(id={}, role={}, text={})>".format(
            self.id,
            self.role,
            self.content,
        )


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("instance_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id = Column(Integer, unique=True, default=1)
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
        return "<Settings(id={}, assistant_id={}, thread_id={})>".format(
            self.id,
            self.assistant_id,
            self.thread_id,
        )
