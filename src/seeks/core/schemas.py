from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Component(Enum):
    PROVIDER = "provider"
    AGENT = "agent"
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


class AgentBase(BaseModel):
    name: str
    model: str
    description: str


class AgentCreate(AgentBase):
    pass


class AgentResponse(BaseModel):
    id: int
    name: str
    model: str
    description: str

    class Config:
        from_attributes = True


class ThreadBase(BaseModel):
    name: str
    agent_id: int
    description: str


class ThreadCreate(ThreadBase):
    pass


class ThreadResponse(BaseModel):
    id: int
    name: str
    agent_id: int
    description: str

    class Config:
        from_attributes = True
