import asyncio
import json
import logging
import types
import typing as T

import aiohttp
import websockets

from .base import DeviceBase
from .models import APIPath, Component, Event, Status, parse_component

logger = logging.getLogger(__name__)


class DeviceError(Exception):
    pass


class Device(DeviceBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session = aiohttp.ClientSession()
        self._auto_update_task = None

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
        event = {"name": event_name}
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

    async def start_auto_update(
        self, update_callback: T.Optional[T.Callable[[Component], None]] = None
    ) -> None:
        if self._auto_update_task is not None:
            logger.debug("Auto-update already started!")
            return
        self._auto_update_task = asyncio.create_task(
            self._auto_update(update_callback=update_callback)
        )

    async def stop_auto_update(self):
        if self._auto_update_task is None:
            logger.debug("Auto-update is not running!")
            return
        self._auto_update_task.cancel()
        self._auto_update_task = None

    async def _auto_update(
        self,
        update_callback: T.Optional[T.Callable[[Component], T.Awaitable[None]]] = None,
    ) -> None:
        # Auto-reconnect, see
        # https://websockets.readthedocs.io/en/stable/reference/client.html#websockets.client.connect
        websocket_status_endpoint = self.api_url(APIPath.STATUS, protocol="ws")
        async for websocket in websockets.connect(websocket_status_endpoint):
            try:
                async for message_raw in websocket:
                    message_json = json.loads(message_raw)
                    component = parse_component(message_json)
                    logger.debug(f"{self} updated status for {component}")
                    if update_callback is not None:
                        await update_callback(component)
            except websockets.ConnectionClosed:
                continue
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Exception during auto-update")

    async def close(self):
        await self.session.close()
        if self._auto_update_task is not None:
            await self.stop_auto_update()

    async def __aenter__(self) -> "Device":
        return self

    async def __aexit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[types.TracebackType],
    ) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"Control({self.address}, {self.port})"
