from typing import Dict, List, Optional, Union

from sqlalchemy import select

from seeks.core.database import get_db
from seeks.core.models import Assistant, Model, Provider

# ==============================================================================
# Provider
# ==============================================================================


def list_providers() -> List[Dict[str, Union[int, str]]]:
    db = next(get_db())
    providers = db.query(Provider).all()
    return [
        {
            "id": provider.id,
            "name": provider.name,
            "api_key": provider.api_key,
        }
        for provider in providers
    ]


def query_provider_names() -> List[str]:
    db = next(get_db())
    providers = db.query(Provider).all()
    return [provider.name for provider in providers]


def query_provider_id(name: str) -> Optional[int]:
    db = next(get_db())
    provider = db.query(Provider).filter_by(name=name).first()
    return provider.id if provider else None


def register_provider(name: str, api_key: str) -> None:
    db = next(get_db())
    provider = Provider(name=name, api_key=api_key)
    db.add(provider)
    db.commit()


def unregister_provider(name: str) -> None:
    db = next(get_db())
    provider = db.query(Provider).filter_by(name=name).first()
    db.delete(provider)
    db.commit()


# ==============================================================================
# Model
# ==============================================================================


def list_models() -> List[Dict[str, Union[int, str]]]:
    db = next(get_db())
    query = select(
        Model.id,
        Model.name,
        Provider.name.label("provider"),
    ).join(Provider)
    models = db.execute(query).all()
    return [
        {
            "id": model.id,
            "name": model.name,
            "provider": model.provider,
        }
        for model in models
    ]


def query_model_names() -> List[str]:
    db = next(get_db())
    models = db.query(Model).all()
    return [model.name for model in models]


def query_model_id(name: str) -> Optional[int]:
    db = next(get_db())
    model = db.query(Model).filter_by(name=name).first()
    return model.id if model else None


def register_model(name: str, provider_id: int) -> None:
    db = next(get_db())
    model = Model(name=name, provider_id=provider_id)
    db.add(model)
    db.commit()


def unregister_model(name: str) -> None:
    db = next(get_db())
    provider = db.query(Model).filter_by(name=name).first()
    db.delete(provider)
    db.commit()


# ==============================================================================
# Assistant
# ==============================================================================


def list_assistants() -> List[Dict[str, Union[int, str]]]:
    db = next(get_db())
    query = select(
        Assistant.id,
        Assistant.name,
        Model.name.label("model"),
    ).join(Model)
    assistants = db.execute(query).all()
    return [
        {
            "id": assistant.id,
            "name": assistant.name,
            "model": assistant.model,
        }
        for assistant in assistants
    ]


def query_assistant_names() -> List[str]:
    db = next(get_db())
    assistants = db.query(Assistant).all()
    return [assistant.name for assistant in assistants]


def query_assistant_id(name: str) -> Optional[int]:
    db = next(get_db())
    assistant = db.query(Assistant).filter_by(name=name).first()
    return assistant.id if assistant else None


def register_assistant(name: str, description: str, model_id: int) -> None:
    db = next(get_db())
    assistant = Assistant(name=name, description=description, model_id=model_id)
    db.add(assistant)
    db.commit()


def unregister_assistant(name: str) -> None:
    db = next(get_db())
    assistant = db.query(Assistant).filter_by(name=name).first()
    db.delete(assistant)
    db.commit()
