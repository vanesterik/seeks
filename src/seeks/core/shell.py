import atexit
import cmd
import os
import readline

from seeks.common.config import Config
from seeks.core import schemas
from seeks.core.commands import Commands
from seeks.core.prompts import Prompts
from seeks.utils.ellipse import ellipse
from seeks.utils.get_home_dir import get_home_dir
from seeks.utils.get_project_version import get_project_version
from seeks.utils.mask_api_key import mask_api_key
from seeks.utils.print import print_alert, print_table


class Shell(cmd.Cmd):
    def __init__(
        self,
        commands: Commands,
        config: Config,
        prompts: Prompts,
    ) -> None:
        super().__init__()

        self._commands = commands
        self._config = config
        self._history_file = os.path.expanduser(get_home_dir() / "history")
        self._prompts = prompts
        self._init_history()

        self.intro = "{}\n{}\n".format(
            f"SEEKS {get_project_version()}",
            "Type 'help' or '?' for more information.",
        )
        self.prompt = ">>> "

    def _init_history(self) -> None:
        """
        Initialize history file and set history length to 1000 lines to store
        more commands in history file.

        """
        readline.set_history_length(1000)

        try:
            readline.read_history_file(self._history_file)
        except FileNotFoundError:
            pass

        atexit.register(self._save_history)

    def _save_history(self) -> None:
        """
        Save history file when exiting the shell session.

        """
        readline.write_history_file(self._history_file)

    def run(self) -> None:
        """
        Run shell instance and handle KeyboardInterrupt exception to exit shell
        session gracefully.

        """

        # Clear thread setting before running the shell to ensure a clean start.
        self._commands.delete_thread_setting()

        try:
            self.cmdloop()

        except KeyboardInterrupt:
            print("Exiting...")

    def emptyline(self) -> bool:
        """
        Do nothing on empty input line

        """
        return False

    def default(self, prompt: str) -> None:
        """
        Everything which is not a command, is considered to be input for the
        configured settings and will be processed accordingly.

        """

        providers = self._commands.read_providers()

        if not providers:
            print_alert(
                "No providers found. Provider is required to use system.",
                type="error",
            )
            return None

        assistants = self._commands.read_assistants()

        if not assistants:
            print_alert(
                "No assistants found. Assistant is required to use system.",
                type="error",
            )
            return None

        settings = self._commands.read_settings()

        if not settings:
            print_alert(
                "No settings configured. Minimum requirement to use system is to set assistant setting.",
                type="error",
            )
            return None

        thread_id = settings.thread_id

        if thread_id is None:
            thread = self._commands.create_thread(
                schemas.ThreadCreate(
                    subject=prompt,
                    assistant_id=settings.assistant_id,
                )
            )
            thread_id = thread.id
            self._commands.update_settings(thread_id=thread_id)

        self._commands.create_message(
            schemas.MessageCreate(
                thread_id=thread_id,
                role=schemas.Role.USER,
                content=prompt,
            )
        )

    def do_quit(self, _: str) -> bool:
        """
        Quit the program

        """
        return True

    def do_exit(self, _: str) -> bool:
        """
        Same as quit

        """
        return True

    def do_list(self, _: str) -> None:
        """
        Shell command to list component items from database:

        - providers
        - assistants
        - threads

        """

        component = self._prompts.select_component()

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return None

        if component.component == schemas.Component.PROVIDER:
            providers = self._commands.read_providers()

            if not providers:
                print_alert("No providers created", type="warning")
                return None

            providers = [
                schemas.ProviderResponse(
                    id=provider.id,
                    name=self._config.find_provider(provider.name).display_name,
                    api_key=mask_api_key(provider.api_key),
                )
                for provider in providers
            ]
            print_table(providers)

        if component.component == schemas.Component.ASSISTANT:
            assistants = self._commands.read_assistants()

            if not assistants:
                print_alert("No assistants created", type="warning")
                return None

            assistants = [
                schemas.AssistantResponse(
                    id=assistant.id,
                    name=assistant.name,
                    model=assistant.model,
                    description=ellipse(assistant.description),
                )
                for assistant in assistants
            ]
            print_table(assistants)

        if component.component == schemas.Component.THREAD:
            threads = self._commands.read_threads(verbose=True)

            if not threads:
                print_alert("No threads created", type="warning")
                return None

            threads = [
                schemas.ThreadVerboseResponse(
                    id=thread.id,
                    assistant_name=thread.assistant_name,
                    subject=ellipse(thread.subject),
                )
                for thread in threads
            ]
            print_table(threads)

        if component.component == schemas.Component.SETTINGS:
            settings = self._commands.read_settings(verbose=True)

            if not settings:
                print_alert("No settings created", type="warning")
                return None

            settings = [
                schemas.SettingsVerboseResponse(
                    id=settings.id,
                    assistant_name=settings.assistant_name,
                    thread_subject=ellipse(settings.thread_subject),
                )
            ]
            print_table(settings)

    def do_create(self, _: str) -> None:
        """
        Shell command to create component entry in database:

        - provider
        - assistant

        Remarks
        -------
        - Threads are excluded as these are created by user input in the default
          flow of the application.

        """

        component = self._prompts.select_component(
            exclude=[
                schemas.Component.THREAD,
                schemas.Component.SETTINGS,
            ]
        )

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return None

        if component.component == schemas.Component.PROVIDER:
            provider = self._prompts.create_provider()

            if provider is None:
                print_alert("Provider creation cancelled", type="warning")
                return None

            try:
                self._commands.create_provider(provider)
                print_alert("Provider created", type="success")

            except ValueError as error:
                print_alert(str(error), type="error")

        if component.component == schemas.Component.ASSISTANT:
            providers = self._commands.read_providers()

            if not providers:
                print_alert(
                    "No providers available to create assistant",
                    type="warning",
                )
                return None

            assistant = self._prompts.create_assistant(providers)

            if assistant is None:
                print_alert("Assistant creation cancelled", type="warning")
                return None

            try:
                self._commands.create_assistant(assistant)
                print_alert("Assistant created", type="success")

            except ValueError as error:
                print_alert(str(error), type="error")

    def do_update(self, _: str) -> None:
        """
        Shell command to update component entry in database:

        - provider
        - assistant
        - settings

        Remarks
        -------

        - Providers can only be updated by provider name, as the API key is not
          allowed to be changed.
        - Threads are excluded as these are created by user input in the default
          flow of the application.
        - Settings follow a different flow as these are updates for the single
          record the settings table holds.

        """

        component = self._prompts.select_component(
            exclude=[
                schemas.Component.THREAD,
            ]
        )

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return None

        if component.component == schemas.Component.PROVIDER:
            providers = self._commands.read_providers()

            if not providers:
                print_alert("No providers to update", type="warning")
                return None

            provider = self._prompts.select_provider(providers)

            if provider is None:
                print_alert("Provider selection cancelled", type="warning")
                return None

            provider = self._prompts.update_provider(provider)

            if provider is None:
                print_alert("Provider update cancelled", type="warning")
                return None

            self._commands.update_provider(provider)
            print_alert("Provider updated", type="success")

        if component.component == schemas.Component.ASSISTANT:
            providers = self._commands.read_providers()

            if not providers:
                print_alert(
                    "No providers available to update assistant",
                    type="warning",
                )
                return None

            assistants = self._commands.read_assistants()

            if not assistants:
                print_alert("No assistants to update", type="warning")
                return None

            assistant = self._prompts.select_assistant(assistants)

            if assistant is None:
                print_alert("Assistant selection cancelled", type="warning")
                return None

            assistant = self._prompts.update_assistant(providers, assistant)

            if assistant is None:
                print_alert("Assistant update cancelled", type="warning")
                return None

            self._commands.update_assistant(assistant)
            print_alert("Assistant updated", type="success")

        if component.component == schemas.Component.SETTINGS:
            component = self._prompts.select_component(
                exclude=[
                    schemas.Component.PROVIDER,
                    schemas.Component.SETTINGS,
                ],
                message="Select setting",
            )

            if component is None:
                print_alert("Setting selection cancelled", type="warning")
                return None

            if component.component == schemas.Component.ASSISTANT:
                assistants = self._commands.read_assistants()

                if not assistants:
                    print_alert("No assistants to set", type="warning")
                    return None

                assistant = self._prompts.select_assistant(assistants)

                if assistant is None:
                    print_alert("Assistant selection cancelled", type="warning")
                    return None

                threads = self._commands.read_threads(assistant_id=assistant.id)

                if not threads:
                    self._commands.update_settings(assistant_id=assistant.id)
                    print_alert("Settings updated", type="success")
                    return None

                thread = self._prompts.select_thread(threads)

                if thread is None:
                    print_alert("Thread selection cancelled", type="warning")
                    return None

                self._commands.update_settings(
                    assistant_id=assistant.id,
                    thread_id=thread.id,
                )
                print_alert("Settings updated", type="success")

            if component.component == schemas.Component.THREAD:
                settings = self._commands.read_settings()

                if not settings:
                    print_alert(
                        "No assistant setting available to set thread",
                        type="warning",
                    )
                    return None

                threads = self._commands.read_threads(
                    assistant_id=settings.assistant_id
                )

                if not threads:
                    print_alert("No threads available", type="warning")
                    return None

                thread = self._prompts.select_thread(threads)

                if thread is None:
                    print_alert("Thread selection cancelled", type="warning")
                    return None

                self._commands.update_settings(thread_id=thread.id)
                print_alert("Settings updated", type="success")

    def do_delete(self, _: str) -> None:
        """
        Shell command to delete component item from database:

        - provider
        - assistant
        - thread

        """

        component = self._prompts.select_component(
            exclude=[
                schemas.Component.SETTINGS,
            ]
        )

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return

        if component.component == schemas.Component.PROVIDER:
            providers = self._commands.read_providers()

            if not providers:
                print_alert("No providerss to delete", type="warning")
                return None

            provider = self._prompts.select_provider(providers)

            if provider is None:
                print_alert("Provider selection cancelled", type="warning")
                return None

            self._commands.delete_provider(provider.id)
            print_alert("Provider deleted", type="success")

        if component.component == schemas.Component.ASSISTANT:
            assistants = self._commands.read_assistants()

            if not assistants:
                print_alert("No assistants to delete", type="warning")
                return None

            assistant = self._prompts.select_assistant(assistants)

            if assistant is None:
                print_alert("Assistant selection cancelled", type="warning")
                return None

            self._commands.delete_assistant(assistant.id)
            print_alert("Assistant deleted", type="success")

        if component.component == schemas.Component.THREAD:
            threads = self._commands.read_threads()

            if not threads:
                print_alert("No threads to delete", type="warning")
                return None

            thread = self._prompts.select_thread(threads)

            if thread is None:
                print_alert("Thread selection cancelled", type="warning")
                return None

            self._commands.delete_thread(thread.id)
            print_alert("Thread deleted", type="success")
