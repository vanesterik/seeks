from typing import List, Optional, Union

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from seeks.core import models, schemas


class Commands:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_provider(self, provider: schemas.ProviderCreate) -> None:
        """
        Create provider.

        Params
        ------
        - provider (ProviderCreate): Provider to create.

        """

        provider = models.Provider(**provider.model_dump())
        self._session.add(provider)

        try:
            self._session.commit()

        except IntegrityError:
            self._session.rollback()
            raise ValueError("Provider already exists")

    def create_assistant(self, assistant: schemas.AssistantCreate) -> None:
        """
        Create assistant.

        Params
        ------
        - assistant (AssistantCreate): Assistant to create.

        """

        assistant = models.Assistant(**assistant.model_dump())
        self._session.add(assistant)

        try:
            self._session.commit()

        except IntegrityError:
            self._session.rollback()
            raise ValueError("Assistant already exists")

    def create_thread(self, thread: schemas.ThreadCreate) -> schemas.ThreadResponse:
        """
        Create thread.

        Params
        ------
        - thread (ThreadCreate): Thread to create.

        Returns
        -------
        - ThreadResponse: Thread created.

        """

        thread = models.Thread(**thread.model_dump())
        self._session.add(thread)
        self._session.commit()
        return schemas.ThreadResponse.model_validate(thread)

    def create_message(self, message: schemas.MessageCreate) -> None:
        """
        Create message.

        Params
        ------
        - message (MessageCreate): Message to create.

        """

        message = models.Message(**message.model_dump())
        self._session.add(message)
        self._session.commit()

    def read_providers(self) -> List[schemas.ProviderResponse]:
        """
        Return all providers.

        Returns
        -------
        - List[ProviderResponse]: Provider(s).

        """

        records = self._session.scalars(select(models.Provider)).all()
        return [schemas.ProviderResponse.model_validate(record) for record in records]

    def read_assistants(self) -> List[schemas.AssistantResponse]:
        """
        Return all assistants.

        Returns
        -------
        - List[AssistantResponse]: Assistant(s).

        """

        records = self._session.scalars(select(models.Assistant)).all()
        return [schemas.AssistantResponse.model_validate(record) for record in records]

    def read_threads(
        self,
        assistant_id: Optional[int] = None,
        verbose: Optional[bool] = False,
    ) -> Union[
        schemas.ThreadResponse,
        List[schemas.ThreadResponse],
        List[schemas.ThreadVerboseResponse],
    ]:
        """
        Return all threads or return threads filtered by assistant id.

        Params
        ------
        - assistant_id (Optional[int]): Assistant id.
        - verbose (Optional[bool]): Return verbose response.

        Returns
        -------
        - Union[ThreadResponse, List[ThreadResponse],
          List[ThreadVerboseResponse]]: Thread(s).

        """

        if assistant_id:
            records = self._session.scalars(
                select(models.Thread).filter_by(assistant_id=assistant_id)
            ).all()
            return [schemas.ThreadResponse.model_validate(record) for record in records]

        records = self._session.scalars(select(models.Thread)).all()

        if verbose:
            return [
                schemas.ThreadVerboseResponse.model_validate(record)
                for record in records
            ]

        return [schemas.ThreadResponse.model_validate(record) for record in records]

    def read_settings(
        self,
        verbose: Optional[bool] = False,
    ) -> Union[schemas.SettingsResponse, None]:
        """
        Return all settings. Return only the first record as it should be
        unique, due its constraints set in the database.

        Returns
        -------
        - SettingsResponse: Settings.

        """

        record = self._session.scalar(select(models.Settings))

        if not record:
            return None

        if verbose:
            return schemas.SettingsVerboseResponse.model_validate(record)

        return schemas.SettingsResponse.model_validate(record)

    def update_provider(self, provider: schemas.ProviderResponse) -> None:
        """
        Update provider by id within passed payload. Only the `api_key` can be
        updated, as the name is a static value defined in the configuration
        file.

        Params
        ------
        - provider (ProviderUpdate): Provider to update.

        """

        record = self._session.get(models.Provider, provider.id)

        if not record:
            return None

        record.api_key = provider.api_key
        self._session.commit()

    def update_assistant(self, assistant: schemas.ProviderResponse) -> None:
        """
        Update assistant by id within passed payload.

        Params
        ------
        - assistant (schemas.AssistantUpdate): Assistant to update.

        """

        record = self._session.get(models.Assistant, assistant.id)

        if not record:
            return None

        record.name = assistant.name
        record.description = assistant.description
        record.model = assistant.model
        self._session.commit()

    def update_settings(
        self,
        assistant_id: Optional[int] = None,
        thread_id: Optional[int] = None,
    ) -> None:
        """
        Update assistant settings.

        Params
        ------
        - assistant_id (int): Assistant id.
        - thread_id (Optional[int]): Thread id.

        """

        record = self._session.scalar(select(models.Settings))

        if not record:
            record = models.Settings()
            self._session.add(record)

        if assistant_id:
            record.assistant_id = assistant_id

        if thread_id:
            record.thread_id = thread_id

        self._session.commit()

    def delete_provider(self, provider_id: int) -> None:
        """
        Delete provider by id.

        Params
        ------
        - provider_id (int): Provider id.

        """

        record = self._session.get(models.Provider, provider_id)
        self._session.delete(record)
        self._session.commit()

    def delete_assistant(self, assistant_id: int) -> None:
        """
        Delete assistant by id.

        Params
        ------
        - assistant_id (int): Assistant id.

        """

        record = self._session.get(models.Assistant, assistant_id)
        self._session.delete(record)
        self._session.commit()

    def delete_thread(self, thread_id: int) -> None:
        """
        Delete thread by id.

        Params
        ------
        - thread_id (int): Thread id.

        """

        record = self._session.get(models.Thread, thread_id)
        self._session.delete(record)
        self._session.commit()

    def delete_thread_setting(self) -> None:
        """
        Delete thread settings.

        """

        record = self._session.scalar(select(models.Settings))

        if not record:
            return None

        record.thread_id = None
        self._session.commit()
