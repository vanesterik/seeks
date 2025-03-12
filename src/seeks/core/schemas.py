from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel


class Component(str, Enum):
    PROVIDER = "provider"
    ASSISTANT = "assistant"
    THREAD = "thread"
    SETTINGS = "settings"

    @classmethod
    def to_list(cls, exclude: Optional[List["Component"]] = None) -> List[str]:
        if exclude is None:
            exclude = []
        return [component.value for component in cls if component not in exclude]


class ComponentSelect(BaseModel):
    component: Component


class ProviderBase(BaseModel):
    name: str
    api_key: str


class ProviderCreate(ProviderBase):
    pass


class ProviderResponse(BaseModel):
    id: int
    name: str
    api_key: str

    class Config:
        from_attributes = True


class AssistantBase(BaseModel):
    name: str
    model: str
    description: str


class AssistantCreate(AssistantBase):
    pass


class AssistantResponse(BaseModel):
    id: int
    name: str
    model: str
    description: str

    class Config:
        from_attributes = True


class ThreadBase(BaseModel):
    subject: str
    assistant_id: int


class ThreadCreate(ThreadBase):
    pass


class ThreadResponse(BaseModel):
    id: int
    assistant_id: int
    subject: str

    class Config:
        from_attributes = True


class ThreadVerboseResponse(BaseModel):
    id: int
    assistant_name: str
    subject: str

    class Config:
        from_attributes = True


class Role(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class MessageBase(BaseModel):
    thread_id: int
    role: Role
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    id: int
    thread_id: int
    role: Role
    content: str

    class Config:
        from_attributes = True


class SettingsResponse(BaseModel):
    id: int
    assistant_id: int
    thread_id: Union[int, None]

    class Config:
        from_attributes = True


class SettingsVerboseResponse(BaseModel):
    id: int
    assistant_name: Union[str, None]
    thread_subject: Union[str, None]

    class Config:
        from_attributes = True
