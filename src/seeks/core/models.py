from typing import List, Union

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from seeks.core.schemas import ProviderName, Role


class Base(DeclarativeBase):
    pass


class Provider(Base):
    __tablename__ = "provider"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[ProviderName] = mapped_column(Enum(ProviderName), unique=True)
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
    model_name: Mapped[str]
    threads: Mapped[List["Thread"]] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )
    settings = relationship("Settings", back_populates="assistant")

    def __repr__(self) -> str:
        return "<Assistant(id={}, name={}, model_name={}, description={})>".format(
            self.id,
            self.name,
            self.model_name,
            self.description,
        )


class Thread(Base):
    __tablename__ = "thread"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str]
    assistant: Mapped["Assistant"] = relationship(back_populates="threads")
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistant.id"))
    messages: Mapped[List["Message"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )
    settings = relationship("Settings", back_populates="thread")

    @hybrid_property
    def assistant_name(self) -> Union[str, None]:
        return self.assistant.name if self.assistant else None

    def __repr__(self) -> str:
        return "<Thread(id={}, subject={})>".format(
            self.id,
            self.subject,
        )


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Role] = mapped_column(Enum(Role))
    content: Mapped[str]
    thread: Mapped["Thread"] = relationship(back_populates="messages")
    thread_id: Mapped[int] = mapped_column(ForeignKey("thread.id"))

    def __repr__(self) -> str:
        return "<Message(id={}, role={}, content={})>".format(
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

    @hybrid_property
    def assistant_name(self) -> Union[str, None]:
        return self.assistant.name if self.assistant else None

    @hybrid_property
    def thread_subject(self) -> Union[str, None]:
        return self.thread.subject if self.thread else None

    def __repr__(self) -> str:
        return "<Settings(id={}, assistant_id={}, thread_id={})>".format(
            self.id,
            self.assistant_id,
            self.thread_id,
        )
