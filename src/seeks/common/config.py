from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from seeks.core import schemas


class ModelDetails(BaseModel):
    name: str
    description: Optional[str]


class ProviderProfile(BaseModel):
    name: schemas.ProviderName
    display_name: str
    endpoint: str
    description: Optional[str]
    models: List[ModelDetails]


class Config(BaseModel):
    providers: List[ProviderProfile] = [
        ProviderProfile(
            name=schemas.ProviderName.ANTHROPIC.value,
            display_name="Anthropic",
            description="Anthropic API",
            endpoint="https://api.anthropic.com/v1/messages",
            models=[
                ModelDetails(
                    name=schemas.ModelName.CLAUDE_3_5_HAIKU_20241022.value,
                    description="Claude 3.5 Haiku model",
                ),
                ModelDetails(
                    name=schemas.ModelName.CLAUDE_3_5_SONNET_20241022.value,
                    description="Claude 3.5 Sonnet model",
                ),
            ],
        ),
        ProviderProfile(
            name=schemas.ProviderName.OPENAI.value,
            display_name="OpenAI",
            description="OpenAI API",
            endpoint="https://api.openai.com/v1/chat/completions",
            models=[
                ModelDetails(
                    name=schemas.ModelName.O3_MINI.value,
                    description="OpenAI o1 model",
                ),
                ModelDetails(
                    name=schemas.ModelName.GPT_4O.value,
                    description="GPT-4o model",
                ),
            ],
        ),
    ]

    def find_provider_by_name(
        self, name: schemas.ProviderName
    ) -> Union[ProviderProfile, None]:
        """
        Find provider by name.

        Params
        ------
        - name (str): Provider name.

        Returns
        -------
        - Union[ProviderProfile, None]: Provider profile.

        """

        for provider in self.providers:
            if provider.name == name:
                return provider

        return None

    def find_provider_by_model(self, model: str) -> Union[ProviderProfile, None]:
        """
        Find provider by model.

        Params
        ------
        - model_name (str): Model name.

        Returns
        -------
        - Union[ProviderProfile, None]: Provider profile.

        """

        for provider in self.providers:
            for model_details in provider.models:
                if model_details.name == model:
                    return provider

        return None

    def list_models(self, provider_names: List[schemas.ProviderName]) -> List[str]:
        """
        List all models from provider profiles in flat list, filtered by passed
        provider names.

        Returns
        -------
        - List[str]: List of model names.

        """

        return [
            model.name
            for provider in self.providers
            if provider.name in provider_names
            for model in provider.models
        ]

    def generate_payload(
        self,
        provider: schemas.ProviderResponse,
        assistant: schemas.AssistantResponse,
        messages: List[schemas.MessageResponse],
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """
        Generate payload for provider.

        Params
        ------
        - provider (ProviderProfile): Provider profile.
        - model (str): Model name.
        - prompt (str): Prompt.

        Returns
        -------
        - Tuple[Dict[str, str], Dict[str, Any]]: (headers, data).

        """

        headers = {
            "Content-Type": "application/json",
        }

        data: Dict[str, Any] = {
            "model": assistant.model_name,
            "messages": [
                {
                    "role": message.role.value,
                    "content": message.content,
                }
                for message in messages
            ],
        }

        if provider.name == schemas.ProviderName.ANTHROPIC:
            headers["x-api-key"] = provider.api_key
            data["max_tokens"] = 8192

        if provider.name == schemas.ProviderName.OPENAI:
            headers["Authorization"] = f"Bearer {provider.api_key}"
            data["stream"] = True

        return (headers, data)
