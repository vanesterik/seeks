from typing import List, Optional

from pydantic import BaseModel


class ModelDetails(BaseModel):
    id: str
    name: str
    description: Optional[str]


class ProviderProfile(BaseModel):
    name: str
    display_name: str
    endpoint: str
    description: Optional[str]
    models: List[ModelDetails]


class Config(BaseModel):
    providers: List[ProviderProfile] = [
        ProviderProfile(
            name="anthropic",
            display_name="Anthropic",
            description="Anthropic API",
            endpoint="https://api.anthropic.com/v1/messages",
            models=[
                ModelDetails(
                    id="claude-3-5-haiku-20241022",
                    name="Claude 3.5 Haiku",
                    description="Claude 3.5 Haiku model",
                ),
                ModelDetails(
                    id="claude-3-5-sonnet-20241022",
                    name="Claude 3.5 Sonnet",
                    description="Claude 3.5 Sonnet model",
                ),
            ],
        ),
        ProviderProfile(
            name="openai",
            display_name="OpenAI",
            description="OpenAI API",
            endpoint="https://api.openai.com/v1/chat/completions",
            models=[
                ModelDetails(
                    id="o1-2024-12-17",
                    name="OpenAI o1",
                    description="OpenAI o1 model",
                ),
                ModelDetails(
                    id="gpt-4o",
                    name="GPT-4o",
                    description="GPT-4o model",
                ),
            ],
        ),
    ]

    def find_provider(self, name: str) -> Optional[ProviderProfile]:
        """
        Find provider by name.

        Params
        ------
        - name (str): Provider name.

        Returns
        -------
        - Optional[ProviderProfile]: Provider profile.

        """

        for provider in self.providers:
            if provider.name == name:
                return provider
        return None

    def list_models(self) -> List[str]:
        """
        List all models from all provider profiles in flat list.

        Returns
        -------
        - List[str]: List of model names.

        """
        return [model.name for provider in self.providers for model in provider.models]
