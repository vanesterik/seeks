from seeks.common.config import Config
from seeks.core.commands import Commands
from seeks.core.database import engine, get_session
from seeks.core.models import Base
from seeks.core.prompts import Prompts
from seeks.core.shell import Shell

# from seeks.utils.clear_screen import clear_screen


def main() -> None:
    # clear_screen()

    # Initialize database and tables
    # Base.metadata.drop_all(engine)  # Only for developing/testing purposes
    Base.metadata.create_all(bind=engine)

    config = Config()
    session = next(get_session())
    commands = Commands(session=session)
    prompts = Prompts(config=config)

    # Create and run REPL instance
    shell = Shell(
        commands=commands,
        config=config,
        prompts=prompts,
    )
    shell.run()


if __name__ == "__main__":
    main()
