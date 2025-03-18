import click

from seeks.common.config import Config
from seeks.core.commands import Commands
from seeks.core.database import engine, get_session
from seeks.core.models import Base
from seeks.core.prompts import Prompts
from seeks.core.shell import Shell
from seeks.utils.clear_screen import clear_screen


@click.command()
@click.option("--debug", is_flag=True)
def main(debug: bool = False) -> None:
    # Do not clear screen if in debug mode as it will clear the debugger output
    if not debug:
        clear_screen()

    # Initialize database and tables
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
