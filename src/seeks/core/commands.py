from typing import List, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from seeks.core import models, schemas


class Commands:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_component(self, component: schemas.Component) -> Union[
        List[schemas.ProviderResponse],
        List[schemas.AgentResponse],
        List[schemas.ThreadResponse],
    ]:
        """
        List components.

        Params
        ------
        - component (schemas.Component): Component to list.

        Returns
        -------
        - Union[
            List[schemas.ProviderResponse],
            List[schemas.AgentResponse],
            List[schemas.ThreadResponse],
          ]: List of components.

        """

        if component == schemas.Component.PROVIDER:
            providers = self._session.query(models.Provider).all()
            return [
                schemas.ProviderResponse.model_validate(provider)
                for provider in providers
            ]

        if component == schemas.Component.AGENT:
            agents = self._session.query(models.Agent).all()
            return [schemas.AgentResponse.model_validate(agent) for agent in agents]

        if component == schemas.Component.THREAD:
            threads = self._session.query(models.Thread).all()
            return [schemas.ThreadResponse.model_validate(thread) for thread in threads]

        return []

    def create_component_item(
        self,
        component: schemas.Component,
        component_item: Union[
            schemas.ProviderCreate,
            schemas.AgentCreate,
        ],
    ) -> None:
        """
        Create component item. Only providers and agents are supported, because
        threads are created by default user input.

        Params
        ------
        - component (schemas.Component): Component to create an item for.
        - component_item (Union[
            schemas.ProviderCreate, schemas.AgentCreate,
          ]): Data to create component.

        """

        if component == schemas.Component.PROVIDER:
            provider = models.Provider(**component_item.model_dump())
            self._session.add(provider)
            try:
                self._session.commit()
            except IntegrityError:
                self._session.rollback()
                raise ValueError("Provider already exists")

        if component == schemas.Component.AGENT:
            agent = models.Agent(**component_item.model_dump())
            self._session.add(agent)
            try:
                self._session.commit()
            except IntegrityError:
                self._session.rollback()
                raise ValueError("Agent already exists")

    def read_component_item(
        self, component: schemas.Component, component_item_id: int
    ) -> Union[
        schemas.ProviderResponse,
        schemas.AgentResponse,
        schemas.ThreadResponse,
    ]:
        """
        Read component item.

        Params
        ------
        - component (schemas.Component): Component to read.
        - id (int): Component item id.

        Returns
        -------
        - Union[
            schemas.ProviderResponse,
            schemas.AgentResponse,
            schemas.ThreadResponse,
          ]: Component item.

        """

        if component == schemas.Component.PROVIDER:
            provider = self._session.query(models.Provider).get(component_item_id)
            response = schemas.ProviderResponse.model_validate(provider)

        if component == schemas.Component.AGENT:
            agent = self._session.query(models.Agent).get(component_item_id)
            response = schemas.AgentResponse.model_validate(agent)

        if component == schemas.Component.THREAD:
            thread = self._session.query(models.Thread).get(component_item_id)
            response = schemas.ThreadResponse.model_validate(thread)

        return response

    def update_component_item(
        self,
        component: schemas.Component,
        component_item: Union[
            schemas.ProviderResponse,
            schemas.ProviderResponse,
        ],
    ) -> None:
        """
        Update component item.

        Params
        ------
        - component (schemas.Component): Component to update.
        - id (int): Component item id.
        - component_item (Union[
            schemas.ProviderUpdate, schemas.AgentUpdate,
          ]): Data to update component.

        """

        if component == schemas.Component.PROVIDER:
            provider = self._session.query(models.Provider).get(component_item.id)
            provider.api_key = component_item.api_key
            self._session.commit()

        if component == schemas.Component.AGENT:
            agent = self._session.query(models.Agent).get(component_item.id)
            agent.name = component_item.name
            agent.description = component_item.description
            agent.model = component_item.model
            self._session.commit()

    def delete_component_item(
        self, component: schemas.Component, component_item_id: int
    ) -> None:
        """
        Delete component item.

        Params
        ------
        - component (schemas.Component): Component to delete.
        - id (int): Component item id.

        """

        if component == schemas.Component.PROVIDER:
            provider = self._session.query(models.Provider).get(component_item_id)
            self._session.delete(provider)
            self._session.commit()

        if component == schemas.Component.AGENT:
            agent = self._session.query(models.Agent).get(component_item_id)
            self._session.delete(agent)
            self._session.commit()

        if component == schemas.Component.THREAD:
            thread = self._session.query(models.Thread).get(component_item_id)
            self._session.delete(thread)
            self._session.commit()
