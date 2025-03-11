from typing import List, Literal, Union

from tabulate import tabulate

from seeks.core import schemas
from seeks.utils.clear_screen import clear_screen


def print_alert(
    message: str,
    type: Union[
        Literal["error"],
        Literal["info"],
        Literal["success"],
        Literal["warning"],
    ] = "info",
    clear: bool = True,
) -> None:
    prefix = {
        "error": "\033[91m✖\033[0m",
        "info": "\033[94mi\033[0m",
        "success": "\033[92m✔\033[0m",
        "warning": "\033[93m!\033[0m",
    }

    # Capitalize first letter of message if it's not capitalized
    if not message[0].isupper():
        message = message.capitalize()

    # Add period at the end of message if it doesn't exist
    if not message.endswith("."):
        message += "."

    # Clear screen before printing message
    if clear:
        clear_screen()

    print(f"[{prefix[type]}] {message}\n")


def print_table(
    data: Union[
        List[schemas.ProviderResponse],
        List[schemas.AssistantResponse],
        List[schemas.ThreadResponse],
        List[schemas.SettingsResponse],
    ],
    clear: bool = True,
) -> None:

    # Clear screen before printing message
    if clear:
        clear_screen()

    table = tabulate([item.model_dump() for item in data], headers="keys")
    print(f"{table}\n")
