import atexit
import cmd
import os
import readline

from seeks.common.config import Config
from seeks.core import schemas
from seeks.core.commands import Commands
from seeks.core.prompts import Prompts
from seeks.utils.clear_screen import clear_screen
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

        self.intro = (
            "\n".join(
                [
                    f"SEEKS {get_project_version()}",
                    "Type 'help' or '?' for more information.",
                ]
            )
            + "\n"
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
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("Exiting...")

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
        - agents
        - threads

        """

        component = self._prompts.select_component()

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return None

        component_items = self._commands.list_component(component.component)

        if not component_items:
            print_alert(
                f"No {component.component.value}s registered",
                type="warning",
            )
            return None

        if component.component == schemas.Component.PROVIDER:
            providers = [
                schemas.ProviderResponse(
                    id=provider.id,
                    name=self._config.find_provider(provider.name).display_name,
                    api_key=mask_api_key(provider.api_key),
                )
                for provider in component_items
            ]
            print_table(providers)

        if component.component == schemas.Component.AGENT:
            agents = [
                schemas.AgentResponse(
                    id=agent.id,
                    name=agent.name,
                    model=agent.model,
                    description=ellipse(agent.description),
                )
                for agent in component_items
            ]
            print_table(agents)

        if component.component == schemas.Component.THREAD:
            print_table(component_items)

    def do_create(self, _: str) -> None:
        """
        Shell command to create component entry in database:

        - provider
        - agent

        Remarks
        -------
        - Threads are excluded as these are created by user input in the default
          flow of the application.

        """

        component = self._prompts.select_component(exclude=[schemas.Component.THREAD])

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return None

        if component.component == schemas.Component.PROVIDER:
            provider = self._prompts.create_provider()

            if provider is None:
                print_alert("Provider creation cancelled", type="warning")
                return None

            try:
                self._commands.create_component_item(
                    component=component.component,
                    component_item=provider,
                )
                print_alert("Provider created", type="success")

            except ValueError as error:
                print_alert(str(error), type="error")

        if component.component == schemas.Component.AGENT:
            agent = self._prompts.create_agent()

            if agent is None:
                print_alert("Agent creation cancelled", type="warning")
                return None

            try:
                self._commands.create_component_item(
                    component=component.component,
                    component_item=agent,
                )
                print_alert("Agent created", type="success")

            except ValueError as error:
                print_alert(str(error), type="error")

    def do_update(self, _: str) -> None:
        """
        Shell command to update component entry in database:

        - provider
        - agent

        Remarks
        -------

        - Providers can only be updated by provider name, as the API key is not
          allowed to be changed.
        - Threads are excluded as these are created by user input in the default
          flow of the application.

        """

        component = self._prompts.select_component(exclude=[schemas.Component.THREAD])

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return None

        component_items = self._commands.list_component(component.component)

        if not component_items:
            print_alert(
                f"No {component.component.value}s to update",
                type="warning",
            )
            return None

        component_item = self._prompts.select_component_item(
            component=component.component,
            component_items=component_items,
        )

        if component_item is None:
            print_alert(
                f"{component.component.value} selection cancelled",
                type="warning",
            )
            return None

        if component.component == schemas.Component.PROVIDER:
            provider = self._commands.read_component_item(
                component=component.component,
                component_item_id=component_item.id,
            )
            provider = self._prompts.update_provider(provider)

            if provider is None:
                print_alert("Provider update cancelled", type="warning")
                return None

            self._commands.update_component_item(
                component=component.component,
                component_item=provider,
            )
            print_alert("Provider updated", type="success")

        if component.component == schemas.Component.AGENT:
            agent = self._commands.read_component_item(
                component=component.component,
                component_item_id=component_item.id,
            )
            agent = self._prompts.update_agent(agent)

            if agent is None:
                print_alert("Agent update cancelled", type="warning")
                return None

            self._commands.update_component_item(
                component=component.component,
                component_item=agent,
            )
            print_alert("Agent updated", type="success")

    def do_delete(self, _: str) -> None:
        """
        Shell command to delete component item from database:

        - provider
        - agent
        - thread

        """

        component = self._prompts.select_component()

        if component is None:
            print_alert("Component selection cancelled", type="warning")
            return

        component_items = self._commands.list_component(component.component)

        if not component_items:
            print_alert(
                f"No {component.component.value}s to delete",
                type="warning",
            )
            return None

        component_item = self._prompts.select_component_item(
            component=component.component,
            component_items=component_items,
        )

        if component_item is None:
            print_alert(
                f"{component.component.value} selection cancelled",
                type="warning",
            )
            return None

        self._commands.delete_component_item(
            component=component.component,
            component_item_id=component_item.id,
        )
        print_alert(
            f"{component.component.value} deleted",
            type="success",
        )
