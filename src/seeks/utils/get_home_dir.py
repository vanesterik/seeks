from pathlib import Path


def get_home_dir() -> Path:
    """
    Get the home directory for the application. The home directory is created in
    the user's home directory and is used to store configuration files and other
    application data.

    Returns
    -------
    - (Path): Path to the home directory

    """

    home_dir = Path.home() / ".seeks"
    home_dir.mkdir(parents=True, exist_ok=True)
    return home_dir
