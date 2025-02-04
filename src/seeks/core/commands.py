from typing import Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from seeks.common.labels import Labels
from seeks.core.database import Base, engine, get_database
from seeks.core.models import Assistant, Model, Provider, Settings, Thread
from seeks.utils.ellipse import ellipse
from seeks.utils.mask_api_key import mask_api_key

# ==============================================================================
# General
# ==============================================================================


def initialize_database() -> None:
    # Base.metadata.drop_all(engine)  # Only for developing/testing purposes
    Base.metadata.create_all(bind=engine)

    # Create default data
    insert_default_assistants()
    insert_settings()


# ==============================================================================
# Provider
# ==============================================================================


def list_providers() -> List[Dict[str, Union[int, str]]]:
    database = next(get_database())
    providers = database.query(Provider).all()
    return [
        {
            "id": provider.id,
            "name": provider.name,
            "api_key": mask_api_key(provider.api_key),
        }
        for provider in providers
    ]


def query_provider_names() -> List[str]:
    database = next(get_database())
    providers = database.query(Provider).all()
    return [provider.name for provider in providers]


def query_provider_id(name: str) -> Optional[int]:
    database = next(get_database())
    provider = database.query(Provider).filter_by(name=name).first()
    return provider.id if provider else None


def register_provider(name: str, api_key: str) -> None:
    database = next(get_database())
    provider = Provider(name=name, api_key=api_key)
    database.add(provider)
    try:
        database.commit()
    except IntegrityError:
        database.rollback()
        raise ValueError(Labels.PROVIDER_EXISTS)


def unregister_provider(name: str) -> None:
    database = next(get_database())
    provider = database.query(Provider).filter_by(name=name).first()
    database.delete(provider)
    database.commit()


# ==============================================================================
# Model
# ==============================================================================


def list_models() -> List[Dict[str, Union[int, str]]]:
    database = next(get_database())
    query = select(
        Model.id,
        Model.name,
        Provider.name.label("provider"),
    ).join(Provider)
    models = database.execute(query).all()
    return [
        {
            "id": model.id,
            "name": model.name,
            "provider": model.provider,
        }
        for model in models
    ]


def query_model_names() -> List[str]:
    database = next(get_database())
    models = database.query(Model).all()
    return [model.name for model in models]


def query_model_id(name: str) -> Optional[int]:
    database = next(get_database())
    model = database.query(Model).filter_by(name=name).first()
    return model.id if model else None


def register_model(name: str, provider_id: int) -> None:
    database = next(get_database())
    model = Model(name=name, provider_id=provider_id)
    database.add(model)
    try:
        database.commit()
    except IntegrityError:
        database.rollback()
        raise ValueError(Labels.MODEL_EXISTS)


def unregister_model(name: str) -> None:
    database = next(get_database())
    provider = database.query(Model).filter_by(name=name).first()
    database.delete(provider)
    database.commit()


# ==============================================================================
# Assistant
# ==============================================================================


def insert_default_assistants() -> None:
    default_assistant_id = query_assistant_id(Labels.DEFAULT)

    if default_assistant_id is None:
        register_assistant(
            Labels.DEFAULT,
            description=Labels.DEFAULT_INSTRUCTIONS,
        )


def list_assistants() -> List[Dict[str, Union[int, str]]]:
    database = next(get_database())
    assistants = database.query(Assistant).all()
    return [
        {
            "id": assistant.id,
            "name": assistant.name,
            "description": ellipse(assistant.description),
        }
        for assistant in assistants
    ]


def query_assistant_names() -> List[str]:
    database = next(get_database())
    assistants = database.query(Assistant).all()
    return [assistant.name for assistant in assistants]


def query_assistant_id(name: str) -> Optional[int]:
    database = next(get_database())
    assistant = database.query(Assistant).filter_by(name=name).first()
    return assistant.id if assistant else None


def register_assistant(name: str, description: str) -> None:
    database = next(get_database())
    assistant = Assistant(name=name, description=description)
    database.add(assistant)
    try:
        database.commit()
    except IntegrityError:
        database.rollback()
        raise ValueError(Labels.ASSISTANT_EXISTS)


def unregister_assistant(name: str) -> None:
    database = next(get_database())
    assistant = database.query(Assistant).filter_by(name=name).first()
    database.delete(assistant)
    database.commit()


# ==============================================================================
# Thread
# ==============================================================================


# ==============================================================================
# Settings
# ==============================================================================


def insert_settings() -> None:
    database = next(get_database())
    query = select(Settings).filter_by(instance_id=1)
    settings = database.execute(query).scalar_one_or_none()

    if settings is None:
        settings = Settings(instance_id=1)
        database.add(settings)
        database.commit()

    default_assistant_id = query_assistant_id(Labels.DEFAULT)
    update_settings(assistant_id=default_assistant_id)


def update_settings(
    provider_id: Optional[int] = None,
    model_id: Optional[int] = None,
    assistant_id: Optional[int] = None,
    thread_id: Optional[int] = None,
) -> None:
    database = next(get_database())
    query = select(Settings).filter_by(instance_id=1)
    settings = database.execute(query).scalar_one_or_none()

    components = {
        "provider_id": provider_id,
        "model_id": model_id,
        "assistant_id": assistant_id,
        "thread_id": thread_id,
    }

    for field, value in components.items():
        if value is not None:
            setattr(settings, field, value)

    database.commit()


def query_settings() -> Dict[str, List[str]]:
    database = next(get_database())

    query = (
        select(
            Provider.name.label("provider"),
            Model.name.label("model"),
            Assistant.name.label("assistant"),
            Thread.name.label("thread"),
        )
        .select_from(Settings)
        .outerjoin(Provider, Settings.provider_id == Provider.id)
        .outerjoin(Model, Settings.model_id == Model.id)
        .outerjoin(Assistant, Settings.assistant_id == Assistant.id)
        .outerjoin(Thread, Settings.thread_id == Thread.id)
        .filter(Settings.instance_id == 1)
    )
    settings = database.execute(query).first()

    return {
        "component": [
            "provider",
            "model",
            "assistant",
            "thread",
        ],
        "name": [
            settings.provider if settings.provider else "",
            settings.model if settings.model else "",
            settings.assistant if settings.assistant else "",
            ellipse(settings.thread) if settings.thread else "",
        ],
    }
