from typing import List, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from seeks.core import models, schemas


class Commands:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_component(self, component: schemas.Component) -> Union[
        List[schemas.ProviderResponse],
        List[schemas.AssistantResponse],
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
            List[schemas.AssistantResponse],
            List[schemas.ThreadResponse],
          ]: List of components.

        """

        if component == schemas.Component.PROVIDER:
            providers = self._session.query(models.Provider).all()
            return [
                schemas.ProviderResponse.model_validate(provider)
                for provider in providers
            ]

        if component == schemas.Component.ASSISTANT:
            assistants = self._session.query(models.Assistant).all()
            return [
                schemas.AssistantResponse.model_validate(assistant)
                for assistant in assistants
            ]

        if component == schemas.Component.THREAD:
            threads = self._session.query(models.Thread).all()
            return [schemas.ThreadResponse.model_validate(thread) for thread in threads]

        return []

    def create_component_item(
        self,
        component: schemas.Component,
        component_item: Union[
            schemas.ProviderCreate,
            schemas.AssistantCreate,
        ],
    ) -> None:
        """
        Create component item. Only providers and assistants are supported,
        because threads are created by default user input.

        Params
        ------
        - component (schemas.Component): Component to create an item for.
        - component_item (Union[
            schemas.ProviderCreate, schemas.AssistantCreate,
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

        if component == schemas.Component.ASSISTANT:
            assistant = models.Assistant(**component_item.model_dump())
            self._session.add(assistant)
            try:
                self._session.commit()
            except IntegrityError:
                self._session.rollback()
                raise ValueError("Assistant already exists")

    def read_component_item(
        self, component: schemas.Component, component_item_id: int
    ) -> Union[
        schemas.ProviderResponse,
        schemas.AssistantResponse,
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
            schemas.AssistantResponse,
            schemas.ThreadResponse,
          ]: Component item.

        """

        if component == schemas.Component.PROVIDER:
            provider = self._session.query(models.Provider).get(component_item_id)
            response = schemas.ProviderResponse.model_validate(provider)

        if component == schemas.Component.ASSISTANT:
            assistant = self._session.query(models.Assistant).get(component_item_id)
            response = schemas.AssistantResponse.model_validate(assistant)

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
            schemas.ProviderUpdate, schemas.AssistantUpdate,
          ]): Data to update component.

        """

        if component == schemas.Component.PROVIDER:
            provider = self._session.query(models.Provider).get(component_item.id)
            provider.api_key = component_item.api_key
            self._session.commit()

        if component == schemas.Component.ASSISTANT:
            assistant = self._session.query(models.Assistant).get(component_item.id)
            assistant.name = component_item.name
            assistant.description = component_item.description
            assistant.model = component_item.model
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

        if component == schemas.Component.ASSISTANT:
            assistant = self._session.query(models.Assistant).get(component_item_id)
            self._session.delete(assistant)
            self._session.commit()

        if component == schemas.Component.THREAD:
            thread = self._session.query(models.Thread).get(component_item_id)
            self._session.delete(thread)
            self._session.commit()
