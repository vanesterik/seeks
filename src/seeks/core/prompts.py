from typing import Any, List

from inquirer import List as ListPrompt
from inquirer import Text as TextPrompt
from inquirer import prompt

from seeks.core.schemas import (
    AssistantDetails,
    Component,
    ComponentSelection,
    ModelDetails,
    ModelSelection,
    ProviderDetails,
    ProviderSelection,
)


def required(_: Any, current: str) -> bool:
    return current != ""


def select_component() -> ComponentSelection:
    questions = [
        ListPrompt(
            name="component",
            message="Component",
            choices=Component.to_list(),
        )
    ]
    return ComponentSelection(**prompt(questions))


# ==============================================================================
# Provider
# ==============================================================================


def get_provider_details() -> ProviderDetails:
    questions = [
        TextPrompt(
            name="name",
            message="Name",
            validate=required,
        ),
        TextPrompt(
            name="api_key",
            message="API Key",
            validate=required,
        ),
    ]
    return ProviderDetails(**prompt(questions))


def select_provider(providers: List[str]) -> ProviderSelection:
    questions = [
        ListPrompt(
            name="name",
            message="Provider",
            choices=providers,
        )
    ]
    return ProviderSelection(**prompt(questions))


# ==============================================================================
# Model
# ==============================================================================


def get_model_details(provider_id: int) -> ModelDetails:
    questions = [
        TextPrompt(
            name="name",
            message="Name",
            validate=required,
        ),
    ]
    return ModelDetails(
        **prompt(questions),
        provider_id=provider_id,
    )


def select_model(models: List[str]) -> ModelSelection:
    questions = [
        ListPrompt(
            name="name",
            message="Model",
            choices=models,
        )
    ]
    return ModelSelection(**prompt(questions))


# ==============================================================================
# Assistant
# ==============================================================================


def get_assistant_details() -> AssistantDetails:
    questions = [
        TextPrompt(
            name="name",
            message="Name",
            validate=required,
        ),
        TextPrompt(
            name="description",
            message="Description",
            validate=required,
        ),
    ]
    return AssistantDetails(**prompt(questions))


def select_assistant(assistants: List[str]) -> AssistantDetails:
    questions = [
        ListPrompt(
            name="name",
            message="Assistant",
            choices=assistants,
        )
    ]
    return AssistantDetails(**prompt(questions))
