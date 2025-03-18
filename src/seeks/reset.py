from os import getenv

from dotenv import find_dotenv, load_dotenv

from seeks.core import schemas
from seeks.core.commands import Commands
from seeks.core.database import engine, get_session
from seeks.core.models import Base
from seeks.utils.print import print_alert


def reset() -> None:
    # Drop all tables if initialized
    Base.metadata.drop_all(engine)
    # Initialize database and tables
    Base.metadata.create_all(bind=engine)

    # Initialize commands
    session = next(get_session())
    commands = Commands(session=session)

    # Seed database with initial data
    commands.create_provider(
        schemas.ProviderCreate(
            name=schemas.ProviderName.OPENAI,
            api_key=getenv("OPENAI_API_KEY"),
        )
    )
    commands.create_assistant(
        schemas.AssistantCreate(
            name="Default Assistant",
            model_name=schemas.ModelName.GPT_4O,
            description="You are an analytical, autoregressive artificial intelligence assistant. Your role is to help in-depth dialogue, comprehensive analysis, and innovative ideation.",
        )
    )
    commands.update_settings(
        assistant_id=1,
    )

    print_alert("Database reset successfully.", "success", clear=False)


if __name__ == "__main__":
    # Find and load .env files automagically
    load_dotenv(find_dotenv())

    # Run main function
    reset()
