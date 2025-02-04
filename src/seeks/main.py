from seeks.common.config import Config
from seeks.common.labels import Labels
from seeks.core.commands import initialize_database
from seeks.core.shell import Shell
from seeks.utils.clear_screen import clear_screen
from seeks.utils.get_project_version import get_project_version


def main() -> None:
    # Initialize database with tables and default data
    initialize_database()

    # Clear screen to make room for shell intro and prompt
    clear_screen()

    # Create and run REPL instance
    shell = Shell()
    shell.intro = (
        "\n".join(
            [
                f"{Labels.TITLE} {get_project_version()}",
                Labels.INTRO,
            ]
        )
        + "\n"
    )
    shell.prompt = f"{Config.PROMPT} "

    # Run shell instance and handle KeyboardInterrupt exception to exit shell
    # session gracefully
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print(Labels.EXITING)


if __name__ == "__main__":
    main()
