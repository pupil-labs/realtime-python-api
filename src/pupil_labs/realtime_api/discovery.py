import asyncio
import logging
import time
import types
from collections.abc import AsyncIterator

from zeroconf import ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from .models import DiscoveredDeviceInfo

logger = logging.getLogger(__name__)


class Network:
    """Network discovery client for finding devices.

    This class manages device discovery on the local network using Zeroconf/Bonjour.
    It maintains a list of discovered devices and provides methods to access them.

    Attributes:
        _devices (dict | None): A dictionary of discovered devices, where the keys are
            device names and the values are DiscoveredDeviceInfo objects.
        _new_devices (asyncio.Queue): A queue to hold newly discovered devices.
        _aiozeroconf (AsyncZeroconf | None): An instance of AsyncZeroconf for network
            discovery.
        _aiobrowser (AsyncServiceBrowser | None): An instance of AsyncServiceBrowser
            for browsing services on the network.
        _open (bool): A flag indicating whether the network discovery client is open.
    """

    def __init__(self) -> None:
        self._devices: dict | None = {}
        self._new_devices: asyncio.Queue[DiscoveredDeviceInfo] = asyncio.Queue()
        self._aiozeroconf: AsyncZeroconf | None = AsyncZeroconf()
        self._aiobrowser: AsyncServiceBrowser | None = AsyncServiceBrowser(
            self._aiozeroconf.zeroconf,
            "_http._tcp.local.",
            handlers=[self._handle_service_change],
        )
        self._open: bool = True

    async def close(self) -> None:
        """Close all network resources.

        This method stops the Zeroconf browser, closes connections, and clears
        the device list.
        """
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
    def devices(self) -> tuple[DiscoveredDeviceInfo, ...]:
        """Return a tuple of discovered devices."""
        return tuple(self._devices.values())

    async def wait_for_new_device(
        self, timeout_seconds: float | None = None
    ) -> DiscoveredDeviceInfo | None:
        """Wait for a new device to be discovered.

        Args:
            timeout_seconds: Maximum time to wait for a new device.
                If None, wait indefinitely.

        Returns:
            Optional[DiscoveredDeviceInfo]: The newly discovered device,
                or None if the timeout was reached.
        """
        try:
            return await asyncio.wait_for(self._new_devices.get(), timeout_seconds)
        except asyncio.TimeoutError:
            return None

    def _handle_service_change(
        self,
        zeroconf: AsyncZeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        """Handle Zeroconf service change events.

        Args:
            zeroconf: Zeroconf instance.
            service_type: Type of the service.
            name: Name of the service.
            state_change: Type of state change event.
        """
        logger.debug(f"{state_change} {name}")
        if is_valid_service_name(name) and state_change in (
            ServiceStateChange.Added,
            ServiceStateChange.Updated,
        ):
            task = asyncio.create_task(
                self._request_info_and_put_new_device(
                    zeroconf, service_type, name, timeout_ms=3000
                )
            )  # RUF006
            task.add_done_callback(
                lambda t: logger.debug(f"Task completed: {t.result()}")
            )

        elif name in self._devices:
            del self._devices[name]

    async def _request_info_and_put_new_device(
        self, zeroconf: AsyncZeroconf, service_type: str, name: str, timeout_ms: int
    ) -> None:
        """Request service information and add the device to the discovered list.

        Args:
            zeroconf: Zeroconf instance.
            service_type: Type of the service.
            name: Name of the service.
            timeout_ms: Timeout for the request in milliseconds.
        """
        info = AsyncServiceInfo(service_type, name)
        if await info.async_request(zeroconf, timeout_ms):
            device = DiscoveredDeviceInfo(
                name,
                info.server,
                info.port,
                [".".join([str(symbol) for symbol in addr]) for addr in info.addresses],
            )
            self._devices[name] = device
            await self._new_devices.put(device)

    async def __aenter__(self) -> "Network":
        """Enter the async context manager.

        Returns:
            Network: This network instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Exception traceback if an exception was raised.
        """
        await self.close()


async def discover_devices(
    timeout_seconds: float | None = None,
) -> AsyncIterator[DiscoveredDeviceInfo]:
    """Use Bonjour to find devices in the local network that serve the Realtime API.

    This function creates a temporary network discovery client and yields
    discovered devices as they are found.

    Args:
        timeout_seconds: Stop after ``timeout_seconds``. If ``None``, run discovery
            forever.

    Yields:
        DiscoveredDeviceInfo: Information about discovered devices.

    Example:
        ```python
        async for device in discover_devices(timeout_seconds=10.0):
            print(f"Found device: {device.name} at {device.addresses[0]}:{device.port}")
        ```
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
    """Check if the service name is valid for Realtime API"""
    return name.split(":")[0] == "PI monitor"
