import atexit
import cmd
import os
import readline
from typing import Optional

from seeks.common.classes import Component
from seeks.core.commands import (
    list_assistants,
    list_models,
    list_providers,
    query_assistant_names,
    query_model_id,
    query_model_names,
    query_provider_id,
    query_provider_names,
    register_assistant,
    register_model,
    register_provider,
    unregister_assistant,
    unregister_model,
    unregister_provider,
)
from seeks.core.prompts import (
    get_assistant_details,
    get_model_details,
    get_provider_details,
    select_assistant,
    select_component,
    select_model,
    select_provider,
)
from seeks.utils.clear_screen import clear_screen
from seeks.utils.get_home_dir import get_home_dir
from seeks.utils.print import print_message, print_table


class Shell(cmd.Cmd):
    def __init__(
        self,
        history_file: Optional[str] = os.path.expanduser(get_home_dir() / "history"),
    ) -> None:
        super().__init__()
        self.history_file = history_file
        self.init_history()

    def init_history(self) -> None:
        """
        Initialize history file and set history length to 1000 lines to store
        more commands in history file.
        """
        readline.set_history_length(1000)
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        atexit.register(self.save_history)

    def save_history(self) -> None:
        """
        Save history file when exiting the shell session.
        """
        readline.write_history_file(self.history_file)

    def do_help(self, arg: str) -> None:
        """List available commands"""

        if arg:
            super().do_help(arg)
        else:
            table = [
                {
                    "command": command,
                    "description": getattr(self, f"do_{command}").__doc__,
                }
                for command in [
                    "help",
                    "register",
                    "unregister",
                    "list",
                    "quit",
                    "exit",
                ]
            ]
            print_table(table)

    def do_register(self, _: str) -> None:
        """Register component to database"""

        selection = select_component()

        if selection.component == Component.PROVIDER:
            provider = get_provider_details()
            register_provider(provider.name, provider.api_key)

        if selection.component == Component.MODEL:
            provider_names = query_provider_names()

            if not provider_names:
                clear_screen()
                print_message(
                    "No providers found. Please register a provider first",
                    type="warning",
                )
                return

            provider = select_provider(provider_names)
            provider_id = query_provider_id(provider.name)
            model = get_model_details(provider_id)
            register_model(model.name, model.provider_id)

        if selection.component == Component.ASSISTANT:
            model_names = query_model_names()

            if not model_names:
                clear_screen()
                print_message(
                    "No models found. Please register a model first",
                    type="warning",
                )
                return

            model = select_model(model_names)
            model_id = query_model_id(model.name)
            assistant = get_assistant_details(model_id)
            register_assistant(
                assistant.name, assistant.description, assistant.model_id
            )

        clear_screen()
        print_message(
            f"{selection.component.value} registered",
            type="success",
        )

    def do_unregister(self, _: str) -> None:
        """Unregister component from database"""

        selection = select_component()

        if selection.component == Component.PROVIDER:
            provider_names = query_provider_names()
            provider = select_provider(provider_names)
            unregister_provider(provider.name)

        if selection.component == Component.MODEL:
            model_names = query_model_names()
            model = select_model(model_names)
            unregister_model(model.name)

        if selection.component == Component.ASSISTANT:
            assistant_names = query_assistant_names()
            assistant = select_assistant(assistant_names)
            unregister_assistant(assistant.name)

        clear_screen()
        print_message(
            f"{selection.component.value} unregistered",
            type="success",
        )

    def do_list(self, _: str) -> None:
        """List component entries from database"""

        selection = select_component()

        clear_screen()

        if selection.component == Component.PROVIDER:
            providers = list_providers()
            (
                print_table(providers)
                if providers
                else print_message("No providers found", type="warning")
            )

        if selection.component == Component.MODEL:
            models = list_models()
            (
                print_table(models)
                if models
                else print_message("No models found", type="warning")
            )

        if selection.component == Component.ASSISTANT:
            assistants = list_assistants()
            (
                print_table(assistants)
                if assistants
                else print_message("No assistants found", type="warning")
            )

    def do_quit(self, _: str) -> bool:
        """Quit the program"""
        return True

    def do_exit(self, _: str) -> bool:
        """Same as quit"""
        return True

    def emptyline(self) -> bool:
        """
        Do nothing on empty input line
        """
        return False

    def default(self, arg: str) -> None:
        """
        Everything which is not a command, is considered to be input for the
        selected model and will be processed accordingly.
        """
        print(f"\n{arg}\n")
