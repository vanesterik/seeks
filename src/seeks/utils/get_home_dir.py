from pathlib import Path


def get_home_dir() -> Path:
    return Path.home() / ".seeks"
