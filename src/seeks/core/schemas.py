from enum import Enum
from typing import List

from pydantic import BaseModel


class Component(Enum):
    PROVIDER = "provider"
    MODEL = "model"
    ASSISTANT = "assistant"

    @classmethod
    def to_list(cls) -> List[str]:
        return [component.value for component in cls]


class ComponentSelection(BaseModel):
    component: Component


# ==============================================================================
# Provider
# ==============================================================================


class ProviderDetails(BaseModel):
    name: str
    api_key: str


class ProviderSelection(BaseModel):
    name: str


# ==============================================================================
# Model
# ==============================================================================


class ModelDetails(BaseModel):
    name: str
    provider_id: int


class ModelSelection(BaseModel):
    name: str


# ==============================================================================
# Assistant
# ==============================================================================


class AssistantDetails(BaseModel):
    name: str
    description: str
    model_id: int


class AssistantSelection(BaseModel):
    name: str
