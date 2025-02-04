from typing import Any, Dict, List, Literal, Union

from tabulate import tabulate


def print_table(data: List[Dict[str, Any]]) -> None:
    table = tabulate(data, headers="keys")
    print(f"{table}\n")


def print_alert(
    message: str,
    type: Union[
        Literal["error"],
        Literal["info"],
        Literal["success"],
        Literal["warning"],
    ] = "info",
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

    print(f"[{prefix[type]}] {message}\n")
