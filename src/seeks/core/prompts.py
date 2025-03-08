from typing import Any, Dict, List, Optional, Union

from questionary import Choice, prompt

from seeks.common.config import Config
from seeks.core import schemas


class Prompts:
    def __init__(self, config: Config) -> None:
        self._config = config

    def select_component(
        self, exclude: Optional[List[schemas.Component]] = None
    ) -> Union[schemas.ComponentSelect, None]:
        """
        Prompt to select a component: - provider - agent - thread

        Params
        ------
        - exclude (Optional[List[schemas.Component]]): Param to exclude
          component from original list. Defaults to None.

        Returns
        -------
        - Union[schemas.ComponentSelect, None]: Selected component or None in
          case user cancels.

        """

        questions = [
            {
                "type": "select",
                "name": "component",
                "message": "Select component",
                "choices": schemas.Component.to_list(exclude=exclude),
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return schemas.ComponentSelect(**result)

    def select_component_item(
        self,
        component: schemas.Component,
        component_items: Union[
            List[schemas.ProviderResponse],
            List[schemas.AgentResponse],
            List[schemas.ThreadResponse],
        ],
    ) -> Union[schemas.ComponentItemSelect, None]:
        """
        Prompt to select a component item from passed list of component items.

        Params
        ------
        - component (schemas.Component): Component to select item from.
        - component_items (Union[
            List[schemas.ProviderResponse],
            List[schemas.AgentResponse],
            List[schemas.ThreadResponse],
          ]): List of component items.

        Returns
        -------
        - Union[schemas.ComponentItemSelect, None]: Selected component item or
          None in case user cancels.

        """

        if component == schemas.Component.PROVIDER:
            choices = [
                Choice(
                    title=self._config.find_provider(provider.name).display_name,
                    value=provider.id,
                )
                for provider in component_items
            ]
            message = "Select provider"

        if component == schemas.Component.AGENT:
            choices = [
                Choice(
                    title=agent.name,
                    value=agent.id,
                )
                for agent in component_items
            ]
            message = "Select agent"

        if component == schemas.Component.THREAD:
            choices = [
                Choice(
                    title=thread.id,
                    value=thread.id,
                )
                for thread in component_items
            ]
            message = "Select thread"

        questions = [
            {
                "type": "select",
                "name": "id",
                "message": message,
                "choices": choices,
            },
        ]

        result = prompt(questions, kbi_msg="")
        if not result:
            return None

        return schemas.ComponentItemSelect(**result)

    def create_provider(self) -> Union[schemas.ProviderCreate, None]:
        """
        Prompt to create provider.

        Returns
        -------
        - Union[schemas.ProviderCreate, None]: Provider name and API key or None
          in case user cancels.

        """

        choices: List[Choice] = [
            Choice(
                title=provider.display_name,
                value=provider.name,
            )
            for provider in self._config.providers
        ]
        questions: List[Dict[str, Any]] = [
            {
                "type": "select",
                "name": "name",
                "message": "Select provider",
                "choices": choices,
            },
            {
                "type": "text",
                "name": "api_key",
                "message": "API Key",
                "validate": required,
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return schemas.ProviderCreate(**result)

    def create_agent(self) -> Union[schemas.AgentCreate, None]:
        """
        Prompt to create agent.

        Returns
        -------
        - Union[schemas.AgentCreate, None]: Agent name, model and description or
          None in case user cancels.

        """

        questions = [
            {
                "type": "text",
                "name": "name",
                "message": "Agent name",
                "validate": required,
            },
            {
                "type": "select",
                "name": "model",
                "message": "Model",
                "choices": self._config.list_models(),
            },
            {
                "type": "text",
                "name": "description",
                "message": "Description",
                "validate": required,
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return schemas.AgentCreate(**result)

    def update_provider(
        self, provider: schemas.ProviderResponse
    ) -> Union[schemas.ProviderResponse, None]:
        """
        Prompt to update provider.

        Returns
        -------
        - Union[schemas.ProviderResponse, None]: Provider name and API key or
          None in case user cancels.

        """

        questions = [
            {
                "type": "text",
                "name": "api_key",
                "message": "API Key",
                "validate": required,
            },
        ]
        provider_data = provider.model_dump()
        result = prompt(questions)

        if not result:
            return None

        return schemas.ProviderResponse(**{**provider_data, **result})

    def update_agent(
        self, agent: schemas.AgentResponse
    ) -> Union[schemas.AgentResponse, None]:
        """
        Prompt to update agent.

        Returns
        -------
        - Union[schemas.AgentResponse, None]: Agent name, model and description
          or None in case user cancels.

        """

        questions = [
            {
                "type": "text",
                "name": "name",
                "message": "Agent name",
                "validate": required,
                "default": agent.name,
            },
            {
                "type": "select",
                "name": "model",
                "message": "Model",
                "choices": self._config.list_models(),
                "default": agent.model,
            },
            {
                "type": "text",
                "name": "description",
                "message": "Description",
                "validate": required,
                "default": agent.description,
            },
        ]
        agent_data = agent.model_dump()
        result = prompt(questions)

        if not result:
            return None

        return schemas.AgentResponse(**{**agent_data, **result})


def required(value: str) -> bool:
    return value != ""
