import asyncio
import typing as T

from .device import Device
from ..discovery import discover_one_device as _discover_one_device_async
from ..discovery import discover_devices as _discover_devices_async
from ..models import DiscoveredDeviceInfo


def discover_devices(search_duration_seconds: float) -> T.List[Device]:
    """Return all devices that could be found in the given search duration."""

    async def _collect_device_information() -> T.List[DiscoveredDeviceInfo]:
        return [
            dev_info
            async for dev_info in _discover_devices_async(search_duration_seconds)
        ]

    return [
        Device.from_discovered_device(dev_info)
        for dev_info in asyncio.run(_collect_device_information())
    ]


def discover_one_device(
    max_search_duration_seconds: T.Optional[float],
) -> T.Optional[Device]:
    """Search until one device is found."""
    dev_info = asyncio.run(_discover_one_device_async(max_search_duration_seconds))
    if dev_info is not None:
        return Device.from_discovered_device(dev_info)
    return None
