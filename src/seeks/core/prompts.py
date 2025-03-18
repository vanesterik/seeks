from typing import Any, Dict, List, Optional, Union

from questionary import Choice, prompt

from seeks.common.config import Config
from seeks.core import schemas


class Prompts:
    def __init__(self, config: Config) -> None:
        self._config = config

    def select_component(
        self,
        exclude: Optional[List[schemas.Component]] = None,
        message: str = "Select component",
    ) -> Union[schemas.ComponentSelect, None]:
        """
        Prompt to select a component:

        - provider
        - assistant
        - thread
        - settings

        Params
        ------
        - exclude (Optional[List[schemas.Component]]): Param to exclude
          component from original list. Defaults to None.
        - message (str): Message to display in prompt. Defaults to "Select
          component".

        Returns
        -------
        - Union[schemas.ComponentSelect, None]: Selected component or None in
          case user cancels.

        """

        questions = [
            {
                "type": "select",
                "name": "component",
                "message": message,
                "choices": schemas.Component.to_list(exclude),
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return schemas.ComponentSelect(**result)

    def select_provider(
        self, providers: List[schemas.ProviderResponse]
    ) -> Union[schemas.ProviderResponse, None]:
        """
        Prompt to select provider.

        Params
        ------
        - providers (List[schemas.ProviderResponse]): List of providers.

        Returns
        -------
        - Union[schemas.ProviderResponse, None]: Selected provider or None in
          case user cancels.

        """

        choices = [
            Choice(
                title=self._config.find_provider_by_name(provider.name).display_name,
                value=provider.id,
            )
            for provider in providers
        ]
        questions = [
            {
                "type": "select",
                "name": "id",
                "message": "Select provider",
                "choices": choices,
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return next(provider for provider in providers if provider.id == result["id"])

    def select_assistant(
        self, assistants: List[schemas.AssistantResponse]
    ) -> Union[schemas.AssistantResponse, None]:
        """
        Prompt to select assistant.

        Params
        ------
        - assistants (List[schemas.AssistantResponse]): List of assistants.

        Returns
        -------
        - Union[schemas.AssistantResponse, None]: Selected assistant or None in
          case user cancels.

        """

        choices = [
            Choice(
                title=assistant.name,
                value=assistant.id,
            )
            for assistant in assistants
        ]
        questions = [
            {
                "type": "select",
                "name": "id",
                "message": "Select assistant",
                "choices": choices,
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return next(
            assistant for assistant in assistants if assistant.id == result["id"]
        )

    def select_thread(
        self, threads: List[schemas.ThreadResponse]
    ) -> Union[schemas.ThreadResponse, None]:
        """
        Prompt to select thread.

        Params
        ------
        - threads (List[schemas.ThreadResponse]): List of threads.

        Returns
        -------
        - Union[schemas.ThreadResponse, None]: Selected thread or None in
          case user cancels.

        """

        choices = [
            Choice(
                title=thread.subject,
                value=thread.id,
            )
            for thread in threads
        ]
        questions = [
            {
                "type": "select",
                "name": "id",
                "message": "Select thread",
                "choices": choices,
            },
        ]
        result = prompt(questions, kbi_msg="")

        if not result:
            return None

        return next(thread for thread in threads if thread.id == result["id"])

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

    def create_assistant(
        self, providers: List[schemas.ProviderResponse]
    ) -> Union[schemas.AssistantCreate, None]:
        """
        Prompt to create assistant.

        Returns
        -------
        - Union[schemas.AssistantCreate, None]: Assistant name, model and
          description or None in case user cancels.

        """

        provider_names = [provider.name for provider in providers]
        questions = [
            {
                "type": "text",
                "name": "name",
                "message": "Assistant name",
                "validate": required,
            },
            {
                "type": "select",
                "name": "model_name",
                "message": "Model name",
                "choices": self._config.list_models(provider_names),
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

        return schemas.AssistantCreate(**result)

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

    def update_assistant(
        self,
        providers: List[schemas.ProviderResponse],
        assistant: schemas.AssistantResponse,
    ) -> Union[schemas.AssistantResponse, None]:
        """
        Prompt to update assistant.

        Returns
        -------
        - Union[schemas.AssistantResponse, None]: Assistant name, model and
          description or None in case user cancels.

        """

        provider_names = [provider.name for provider in providers]
        questions = [
            {
                "type": "text",
                "name": "name",
                "message": "Assistant name",
                "validate": required,
                "default": assistant.name,
            },
            {
                "type": "select",
                "name": "model",
                "message": "Model",
                "choices": self._config.list_models(provider_names),
                "default": assistant.model_name,
            },
            {
                "type": "text",
                "name": "description",
                "message": "Description",
                "validate": required,
                "default": assistant.description,
            },
        ]
        assistant_data = assistant.model_dump()
        result = prompt(questions)

        if not result:
            return None

        return schemas.AssistantResponse(**{**assistant_data, **result})


def required(value: str) -> bool:
    return value != ""
