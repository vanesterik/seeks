import os
import sys


def clear_screen() -> None:
    # For Windows
    if sys.platform.startswith("win"):
        os.system("cls")
    # For macOS and Linux
    else:
        os.system("clear")
