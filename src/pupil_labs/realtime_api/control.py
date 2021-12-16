import asyncio
import enum
import logging
import types
import typing as T

import aiohttp

from pupil_labs.realtime_api.models import DiscoveredDevice, Status

logger = logging.getLogger(__name__)


class Path(enum.Enum):
    PREFIX = "/api"
    STATUS = "/status"


class Control:
    @classmethod
    def for_discovered_device(cls, device: DiscoveredDevice) -> "Control":
        return cls(device.addresses[0], device.port)

    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port
        self.session = aiohttp.ClientSession()

    async def get_status(self):
        url = f"http://{self.address}:{self.port}{Path.PREFIX.value}{Path.STATUS.value}"
        async with self.session.get(url) as response:
            result = (await response.json())["result"]
            logger.debug(f"Received status: {result}")
            return Status.from_dict(result)

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def print_status():
        async with Control("pi.local", 8080) as control:
            status = await control.get_status()

            print(f"{status.phone.ip=}")

            world = status.direct_world_sensor()
            print(f"{world.connected=} {world.url=}")

            gaze = status.direct_gaze_sensor()
            print(f"{gaze.connected=} {gaze.url=}")

    asyncio.run(print_status())
