import asyncio
import inspect
import json
import logging
import sys
import types
import typing as T
from dataclasses import fields

if sys.version_info[:2] < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

import aiohttp
import websockets

import pupil_labs  # noqa: F401

from .base import DeviceBase
from .camera_control import (
    CameraState,
    ChangeRequestParameters,
    Control,
    ControlStateEnum,
    ControlStateInteger,
    ControlStateResponseEnvelope,
)
from .models import (
    APIPath,
    Component,
    Event,
    Status,
    UnknownComponentError,
    parse_component,
)

logger = logging.getLogger(__name__)

UpdateCallbackSync = T.Callable[['pupil_labs.realtime_api.models.Component'], None]
"""Type annotation for synchronous update callbacks"""

UpdateCallbackAsync = T.Callable[
    ['pupil_labs.realtime_api.models.Component'], T.Awaitable[None]
]
"""Type annotation for asynchronous update callbacks"""

UpdateCallback = T.Union[UpdateCallbackSync, UpdateCallbackAsync]
"""Type annotation for synchronous and asynchronous callbacks"""

ControlStateClass = T.TypeVar(
    "ControlStateClass", ControlStateEnum, ControlStateInteger
)


class DeviceError(Exception):
    pass


class Device(DeviceBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._create_client_session()

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

    async def _set_camera_state(
        self,
        ae_mode: T.Optional[Literal["auto", "manual"]] = None,
        man_exp: T.Optional[int] = None,
        gain: T.Optional[int] = None,
        brightness: T.Optional[int] = None,
        contrast: T.Optional[int] = None,
        gamma: T.Optional[int] = None,
        camera: Literal["world"] = "world",
        validate_with_state: T.Optional[CameraState] = None,
    ) -> None:
        """
        EXPERIMENTAL - Set camera control state, e.g. manual exposure time

        :raises pupil_labs.realtime_api.device.DeviceError:
        :raises aiohttp.ServerDisconnectedError:
        """
        params: ChangeRequestParameters = {"camera": camera}

        self.__prepare_control_param(
            params,
            ae_mode,
            Control.AUTOEXPOSURE_MODE,
            validate_with_state.ae_mode if validate_with_state else None,
        )
        self.__prepare_control_param(
            params,
            man_exp,
            Control.MANUAL_EXPOSURE_TIME,
            validate_with_state.man_exp if validate_with_state else None,
        )
        self.__prepare_control_param(
            params,
            gain,
            Control.GAIN,
            validate_with_state.gain if validate_with_state else None,
        )
        self.__prepare_control_param(
            params,
            brightness,
            Control.BRIGHTNESS,
            validate_with_state.brightness if validate_with_state else None,
        )
        self.__prepare_control_param(
            params,
            contrast,
            Control.CONTRAST,
            validate_with_state.contrast if validate_with_state else None,
        )
        self.__prepare_control_param(
            params,
            gamma,
            Control.GAMMA,
            validate_with_state.gamma if validate_with_state else None,
        )

        async with self.session.post(
            self.api_url(APIPath.CAMERA_CONTROL), params=params
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.camera_control] Received response: {confirmation}")
            if response.status != 200:
                raise DeviceError(response.status, confirmation["message"])

    async def _get_camera_state(
        self,
        camera: Literal["world"] = "world",
    ) -> CameraState:
        """
        EXPERIMENTAL - Get camera control state, e.g. manual exposure time

        :raises pupil_labs.realtime_api.device.DeviceError:
        :raises aiohttp.ServerDisconnectedError:
        """
        return CameraState(
            ae_mode=await self.__get_control_state(
                Control.AUTOEXPOSURE_MODE, ControlStateEnum, camera
            ),
            man_exp=await self.__get_control_state(
                Control.MANUAL_EXPOSURE_TIME, ControlStateInteger, camera
            ),
            contrast=await self.__get_control_state(
                Control.CONTRAST, ControlStateInteger, camera
            ),
            brightness=await self.__get_control_state(
                Control.BRIGHTNESS, ControlStateInteger, camera
            ),
            gain=await self.__get_control_state(
                Control.GAIN, ControlStateInteger, camera
            ),
            gamma=await self.__get_control_state(
                Control.GAMMA, ControlStateInteger, camera
            ),
        )

    async def __get_control_state(
        self,
        control: Control,
        state_cls: T.Type[ControlStateClass],
        camera: Literal["world"] = "world",
    ) -> ControlStateClass:
        params: ChangeRequestParameters = {"camera": camera, control.value: ""}
        async with self.session.get(
            self.api_url(APIPath.CAMERA_CONTROL), params=params
        ) as response:
            if response.status == 404:
                raise DeviceError(
                    response.status, f"Camera {camera} might not be connected"
                )
            envelope: ControlStateResponseEnvelope = await response.json()
            logger.debug(
                f"[{self}._camera_control_state] Received envelope: {envelope}"
            )
            if response.status != 200:
                raise DeviceError(response.status, envelope["message"])

            field_names = tuple(f.name for f in fields(state_cls))
            return state_cls(
                **{k: v for k, v in envelope["result"].items() if k in field_names}
            )

    @staticmethod
    @T.overload
    def __prepare_control_param(
        params: ChangeRequestParameters,
        value: T.Optional[int],
        ctrl: Control,
        state: T.Optional[ControlStateInteger] = None,
    ) -> None:
        ...

    @staticmethod
    @T.overload
    def __prepare_control_param(
        params: ChangeRequestParameters,
        value: T.Optional[str],
        ctrl: Control,
        state: T.Optional[ControlStateEnum] = None,
    ) -> None:
        ...

    @staticmethod
    def __prepare_control_param(
        params: ChangeRequestParameters,
        value: T.Any,
        ctrl: T.Any,
        state: T.Optional[T.Any] = None,
    ) -> None:
        if value is not None:
            if state is not None:
                state.validate(value)
            params[ctrl.value] = value


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
