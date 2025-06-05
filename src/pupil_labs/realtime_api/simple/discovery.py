import asyncio
import logging

from ..discovery import DiscoveredDeviceInfo
from ..discovery import Network as AsyncNetwork
from .device import Device

logger = logging.getLogger(__name__)


def discover_devices(search_duration_seconds: float) -> list[Device]:
    """Discover all available devices on the local network.

    This function searches for devices on the local network for the specified
    duration and returns all discovered devices.

    Args:
        search_duration_seconds: How long to search for devices in seconds.

    Returns:
        list[Device]: List of discovered devices.

    Example:
        ```python
        # Discover devices for 5 seconds
        devices = discover_devices(5.0)
        for device in devices:
            print(f"Found device: {device.phone_name}")
        ```

    See Also:
        The asynchronous equivalent
        :func:`pupil_labs.realtime_api.discovery.discover_devices`

    """

    async def _discover() -> tuple[DiscoveredDeviceInfo, ...]:
        async with AsyncNetwork() as network:
            await asyncio.sleep(search_duration_seconds)
            return network.devices

    return [Device.from_discovered_device(dev) for dev in asyncio.run(_discover())]


def discover_one_device(
    max_search_duration_seconds: float | None = 10.0,
) -> Device | None:
    """Discover and return the first device found on the local network.

    This function searches for devices on the local network and returns
    the first discovered device, or None if no device is found within
    the specified maximum search duration.

    Args:
        max_search_duration_seconds: Maximum time to search for a device in seconds.
            If None, search indefinitely. Default is 10.0 seconds.

    Returns:
        Device or None: The first discovered device, or None if no device was found
        within the specified time limit.

    Example:
        ```python
        # Try to find a device within 5 seconds
        device = discover_one_device(5.0)
        if device:
            print(f"Found device: {device.phone_name}")
        else:
            print("No device found")
        ```

    See Also:
        The asynchronous equivalent
        :func:`pupil_labs.realtime_api.discovery.Network.wait_for_new_device`

    """

    async def _discover() -> DiscoveredDeviceInfo | None:
        async with AsyncNetwork() as network:
            return await network.wait_for_new_device(max_search_duration_seconds)

    device = asyncio.run(_discover())
    return None if device is None else Device.from_discovered_device(device)
