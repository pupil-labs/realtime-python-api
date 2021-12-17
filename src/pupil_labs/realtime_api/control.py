import enum
import logging
import types
import typing as T

import aiohttp

from pupil_labs.realtime_api.models import DiscoveredDevice, Event, Status

logger = logging.getLogger(__name__)


class APIPath(enum.Enum):
    STATUS = "/status"
    RECORDING_START = "/recording:start"
    RECORDING_STOP_AND_SAVE = "/recording:stop_and_save"
    RECORDING_CANCEL = "/recording:cancel"
    EVENT = "/event"


class ControlError(Exception):
    pass


class Control:
    @classmethod
    def for_discovered_device(cls, device: DiscoveredDevice) -> "Control":
        return cls(device.addresses[0], device.port)

    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port
        self.session = aiohttp.ClientSession()

    def api_url(self, path, prefix: str = "/api") -> str:
        return f"http://{self.address}:{self.port}" + prefix + path.value

    async def get_status(self) -> Status:
        async with self.session.get(self.api_url(APIPath.STATUS)) as response:
            confirmation = await response.json()
            if response.status != 200:
                raise ControlError(response.status, confirmation["message"])
            result = confirmation["result"]
            logger.debug(f"[{self}.get_status] Received status: {result}")
            return Status.from_dict(result)

    async def recording_start(self) -> str:
        async with self.session.post(self.api_url(APIPath.RECORDING_START)) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.start_recording] Received response: {confirmation}")
            if response.status != 200:
                raise ControlError(response.status, confirmation["message"])
            return confirmation["result"]["id"]

    async def recording_stop_and_save(self):
        async with self.session.post(
            self.api_url(APIPath.RECORDING_STOP_AND_SAVE)
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.stop_recording] Received response: {confirmation}")
            if response.status != 200:
                raise ControlError(response.status, confirmation["message"])

    async def recording_cancel(self):
        async with self.session.post(
            self.api_url(APIPath.RECORDING_CANCEL)
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.stop_recording] Received response: {confirmation}")
            if response.status != 200:
                raise ControlError(response.status, confirmation["message"])

    async def send_event(
        self, event_name: str, event_timestamp_unix_ns: T.Optional[int] = None
    ) -> Event:
        event = {"name": event_name}
        if event_timestamp_unix_ns is not None:
            event["timestamp"] = event_timestamp_unix_ns

        async with self.session.post(
            self.api_url(APIPath.EVENT), json=event
        ) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.send_event] Received response: {confirmation}")
            if response.status != 200:
                raise ControlError(response.status, confirmation["message"])
            return Event.from_dict(confirmation["result"])

    async def close(self):
        await self.session.close()

    async def __aenter__(self) -> "Control":
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
