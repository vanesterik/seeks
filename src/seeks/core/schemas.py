from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Component(Enum):
    PROVIDER = "provider"
    ASSISTANT = "assistant"
    THREAD = "thread"

    @classmethod
    def to_list(cls, exclude: Optional[List["Component"]]) -> List[str]:
        if exclude is None:
            exclude = []
        return [component.value for component in cls if component not in exclude]


class ComponentSelect(BaseModel):
    component: Component


class ComponentItemSelect(BaseModel):
    id: int


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
    name: str
    assistant_id: int
    description: str


class ThreadCreate(ThreadBase):
    pass


class ThreadResponse(BaseModel):
    id: int
    name: str
    assistant_id: int
    description: str

    class Config:
        from_attributes = True
