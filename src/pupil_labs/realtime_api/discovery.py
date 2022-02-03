import asyncio
import logging
import time
import types
import typing as T

from zeroconf import ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from .models import DiscoveredDeviceInfo

logger = logging.getLogger(__name__)


class Network:
    def __init__(self) -> None:
        self._devices = {}
        self._new_devices = asyncio.Queue()
        self._aiozeroconf = AsyncZeroconf()
        self._aiobrowser = AsyncServiceBrowser(
            self._aiozeroconf.zeroconf,
            "_http._tcp.local.",
            handlers=[self._handle_service_change],
        )
        self._open = True

    async def close(self) -> None:
        if self._open:
            await self._aiobrowser.async_cancel()
            await self._aiozeroconf.async_close()
            self._devices.clear()
            self._devices = None
            while not self._new_devices.empty():
                self._new_devices.get_nowait()
            self._aiobrowser = None
            self._aiozeroconf = None
            self._open = False

    @property
    def devices(self) -> T.Tuple[DiscoveredDeviceInfo, ...]:
        return tuple(self._devices.values())

    async def wait_for_new_device(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[DiscoveredDeviceInfo]:
        try:
            return await asyncio.wait_for(self._new_devices.get(), timeout_seconds)
        except asyncio.TimeoutError:
            return None

    def _handle_service_change(
        self, zeroconf, service_type: str, name: str, state_change: ServiceStateChange
    ) -> None:
        logger.debug(f"{state_change} {name}")
        if is_valid_service_name(name) and state_change in (
            ServiceStateChange.Added,
            ServiceStateChange.Updated,
        ):
            asyncio.create_task(
                self._request_info_and_put_new_device(
                    zeroconf, service_type, name, timeout_ms=3000
                )
            )
        elif name in self._devices:
            del self._devices[name]

    async def _request_info_and_put_new_device(
        self, zeroconf, service_type, name, timeout_ms
    ):
        info = AsyncServiceInfo(service_type, name)
        if await info.async_request(zeroconf, timeout_ms):
            device = DiscoveredDeviceInfo(
                name,
                info.server,
                info.port,
                ['.'.join([str(symbol) for symbol in addr]) for addr in info.addresses],
            )
            self._devices[name] = device
            await self._new_devices.put(device)

    async def __aenter__(self) -> "Network":
        return self

    async def __aexit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[types.TracebackType],
    ):
        await self.close()


async def discover_devices(
    timeout_seconds: T.Optional[float] = None,
) -> T.AsyncIterator[DiscoveredDeviceInfo]:
    """Use Bonjour to find devices in the local network that serve the Realtime API.

    :param timeout_seconds: Stop after ``timeout_seconds``. If ``None``, run discovery
        forever.
    """
    async with Network() as network:
        while True:
            if timeout_seconds is not None and timeout_seconds <= 0.0:
                return
            t0 = time.perf_counter()
            device = await network.wait_for_new_device(timeout_seconds)
            if device is None:
                return  # timeout reached
            else:
                yield device
            if timeout_seconds is not None:
                timeout_seconds -= time.perf_counter() - t0


def is_valid_service_name(name: str) -> bool:
    return name.split(":")[0] == "PI monitor"
