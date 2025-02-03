from seeks.core.database import Base, engine
from seeks.core.shell import Shell
from seeks.utils.clear_screen import clear_screen
from seeks.utils.get_project_version import get_project_version


def main() -> None:

    # Drop all tables
    # Base.metadata.drop_all(engine)

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Clear screen
    clear_screen()

    # Create and run REPL instance
    shell = Shell()
    shell.intro = (
        f"SEEKS {get_project_version()}\nType 'help' or '?' for more information.\n"
    )
    shell.prompt = ">>> "

    # Run shell instance and handle KeyboardInterrupt exception to exit shell
    # session gracefully
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
