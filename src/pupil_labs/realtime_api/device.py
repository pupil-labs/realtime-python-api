import asyncio
import inspect
import json
import logging
import types
import typing as T
from uuid import UUID

import aiohttp
import numpy as np
import websockets
from pupil_labs.neon_recording.calib import Calibration

import pupil_labs  # noqa: F401

from .base import DeviceBase
from .models import (
    APIPath,
    Component,
    Event,
    Status,
    Template,
    TemplateDataFormat,
    UnknownComponentError,
    parse_component,
)

logger = logging.getLogger(__name__)

UpdateCallbackSync = T.Callable[["pupil_labs.realtime_api.models.Component"], None]
"""Type annotation for synchronous update callbacks"""

UpdateCallbackAsync = T.Callable[
    ["pupil_labs.realtime_api.models.Component"], T.Awaitable[None]
]
"""Type annotation for asynchronous update callbacks"""

UpdateCallback = T.Union[UpdateCallbackSync, UpdateCallbackAsync]
"""Type annotation for synchronous and asynchronous callbacks"""


class DeviceError(Exception):
    pass


class Device(DeviceBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._create_client_session()
        self.template_definition: T.Optional[Template] = None

    async def get_status(self) -> Status:
        """
        :raises pupil_labs.realtime_api.device.DeviceError: if the request fails
        """
        async with self.session.get(self.api_url(APIPath.STATUS)) as response:
            confirmation = await response.json()
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])
            result = confirmation["result"]
            logger.debug(f"[{self}.get_status] Received status: {result}")
            return Status.from_dict(result)

    async def status_updates(self) -> T.AsyncIterator[Component]:
        # Auto-reconnect, see
        # https://websockets.readthedocs.io/en/stable/reference/client.html#websockets.client.connect
        websocket_status_endpoint = self.api_url(APIPath.STATUS, protocol="ws")
        async for websocket in websockets.connect(websocket_status_endpoint):
            try:
                async for message_raw in websocket:
                    message_json = json.loads(message_raw)
                    try:
                        component = parse_component(message_json)
                    except UnknownComponentError:
                        logger.warning(f"Dropping unknown component: {component}")
                        continue
                    yield component
            except websockets.ConnectionClosed:
                logger.debug("Websocket connection closed. Reconnecting...")
                continue
            except asyncio.CancelledError:
                logger.debug("status_updates() cancelled")
                break

    async def recording_start(self) -> str:
        """
        :raises pupil_labs.realtime_api.device.DeviceError:
            if the recording could not be started. Possible reasons include
            - Recording already running
            - Template has required fields
            - Low battery
            - Low storage
            - No wearer selected
            - No workspace selected
            - Setup bottom sheets not completed
        """
        async with self.session.post(self.api_url(APIPath.RECORDING_START)) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.start_recording] Received response: {confirmation}")
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])
            return confirmation["result"]["id"]

    async def recording_stop_and_save(self):
        """
        :raises pupil_labs.realtime_api.device.DeviceError:
            if the recording could not be started
            Possible reasons include
            - Recording not running
            - template has required fields
        """
        async with self.session.post(
            self.api_url(APIPath.RECORDING_STOP_AND_SAVE)
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.stop_recording] Received response: {confirmation}")
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])

    async def recording_cancel(self):
        """
        :raises pupil_labs.realtime_api.device.DeviceError:
            if the recording could not be started
            Possible reasons include
            - Recording not running
        """
        async with self.session.post(
            self.api_url(APIPath.RECORDING_CANCEL)
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.stop_recording] Received response: {confirmation}")
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])

    async def send_event(
        self, event_name: str, event_timestamp_unix_ns: T.Optional[int] = None
    ) -> Event:
        """
        :raises pupil_labs.realtime_api.device.DeviceError: if sending the event fails
        """
        event: T.Dict[str, T.Any] = {"name": event_name}
        if event_timestamp_unix_ns is not None:
            event["timestamp"] = event_timestamp_unix_ns

        async with self.session.post(
            self.api_url(APIPath.EVENT), json=event
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.send_event] Received response: {confirmation}")
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])
            return Event.from_dict(confirmation["result"])

    async def get_template(self) -> Template:
        """
        Gets the template currently selected on device

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the template can't be fetched.
        """
        async with self.session.get(
            self.api_url(APIPath.TEMPLATE_DEFINITION)
        ) as response:
            confirmation = await response.json()
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])
            result = confirmation["result"]
            logger.debug(f"[{self}.get_template_def] Received template def: {result}")
            self.template_definition = Template(**result)
            return self.template_definition

    async def get_template_data(self, format: TemplateDataFormat = "simple"):
        """
        Gets the template data entered on device

        :param str format: "simple" | "api"
            "api" returns the data as is from the api eg. {"item_uuid": ["42"]}
            "simple" returns the data parsed eg. {"item_uuid": 42}

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the template's data could not be fetched
        """
        assert (
            format in TemplateDataFormat.__args__
        ), f"format should be one of {TemplateDataFormat}"

        self.template_definition = await self.get_template()

        async with self.session.get(self.api_url(APIPath.TEMPLATE_DATA)) as response:
            confirmation = await response.json()
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])
            result = confirmation["result"]
            logger.debug(
                f"[{self}.get_template_data] Received data's template: {result}"
            )
            if format == "api":
                return result
            elif format == "simple":
                return self.template_definition.convert_from_api_to_simple_format(
                    result
                )

    async def post_template_data(
        self,
        template_answers: T.Dict[str, T.List[str]],
        format: TemplateDataFormat = "simple",
    ) -> None:
        """
        Sets the data for the currently selected template

        :param str format: "simple" | "api"
            "api" accepts the data as in realtime api format eg. {"item_uuid": ["42"]}
            "simple" accepts the data in parsed format eg. {"item_uuid": 42}

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the data can not be sent.
            ValueError: if invalid data type.
        """
        assert (
            format in TemplateDataFormat.__args__
        ), f"format should be one of {TemplateDataFormat}"

        self.template_definition = await self.get_template()

        if format == "simple":
            template_answers = (
                self.template_definition.convert_from_simple_to_api_format(
                    template_answers
                )
            )

        pre_populated_data = await self.get_template_data(format="api")
        errors = self.template_definition.validate_answers(
            pre_populated_data | template_answers, format="api"
        )
        if errors:
            raise ValueError(errors=errors)

        # workaround for issue with api as it fails when passing in an empty list
        # ie. it wants [""] instead of []
        template_answers = {
            key: value if value else [""] for key, value in template_answers.items()
        }

        async with self.session.post(
            self.api_url(APIPath.TEMPLATE_DATA), json=template_answers
        ) as response:
            confirmation = await response.json()
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])
            result = confirmation["result"]
            logger.debug(f"[{self}.get_template_data] Send data's template: {result}")
            return result

    async def get_question_by_id(self, question_id: T.Union[str, UUID]):
        item = (
            self.template_definition.get_question_by_id(question_id)
            if self.template_definition
            else None
        )

        if item:
            return item

        old_template = self.template_definition if self.template_definition else None

        await self.get_template()

        if (
            self.template_definition is not None
            and self.template_definition is not old_template
        ):
            return self.template_definition.get_question_by_id(question_id)

        return None

    async def close(self):
        await self.session.close()
        self.session = None

    async def __aenter__(self) -> "Device":
        if self.session is None:
            self._create_client_session()
        return self

    async def __aexit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[types.TracebackType],
    ) -> None:
        await self.close()

    def _create_client_session(self):
        self.session = aiohttp.ClientSession()

    async def get_calibration(self) -> np.ndarray:
        """
        :raises pupil_labs.realtime_api.device.DeviceError: if the request fails
        """
        async with self.session.get(self.api_url(APIPath.CALIBRATION)) as response:
            if response.status != 200:
                raise DeviceError(response.status, "Failed to fetch calibration")

            raw_data = await response.read()
            return Calibration.from_buffer(raw_data)


class StatusUpdateNotifier:
    def __init__(self, device: Device, callbacks: T.List[UpdateCallback]) -> None:
        self._auto_update_task: T.Optional[asyncio.Task] = None
        self._device = device
        self._callbacks = callbacks

    async def receive_updates_start(self) -> None:
        if self._auto_update_task is not None:
            logger.debug("Auto-update already started!")
            return
        self._auto_update_task = asyncio.create_task(self._auto_update())

    async def receive_updates_stop(self):
        if self._auto_update_task is None:
            logger.debug("Auto-update is not running!")
            return
        self._auto_update_task.cancel()
        try:
            # wait for the task to be cancelled
            await self._auto_update_task
        except asyncio.CancelledError:
            pass  # task has been successfully cancelled
        self._auto_update_task = None

    async def __aenter__(self):
        await self.receive_updates_start()

    async def __aexit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[types.TracebackType],
    ):
        await self.receive_updates_stop()

    async def _auto_update(self) -> None:
        async for changed in self._device.status_updates():
            for callback in self._callbacks:
                result = callback(changed)
                if inspect.isawaitable(result):
                    await result
