import asyncio
import logging

from ..discovery import DiscoveredDeviceInfo
from ..discovery import Network as AsyncNetwork
from .device import Device

logger = logging.getLogger(__name__)


def discover_devices(search_duration_seconds: float) -> list[Device]:
    """Return all devices that could be found in the given search duration.

    .. seealso::
        The asynchronous equivalent
        :py:func:`pupil_labs.realtime_api.discovery.discover_devices`
    """

    async def _discover() -> tuple[DiscoveredDeviceInfo, ...]:
        async with AsyncNetwork() as network:
            await asyncio.sleep(search_duration_seconds)
            return network.devices

    return [Device.from_discovered_device(dev) for dev in asyncio.run(_discover())]


def discover_one_device(
    max_search_duration_seconds: float | None = 10.0,
) -> Device | None:
    """Return the first device that could be found in the given search duration.

    .. seealso::
        The asynchronous equivalent
        :py:func:`pupil_labs.realtime_api.discovery.Network.wait_for_new_device`
    """

    async def _discover() -> DiscoveredDeviceInfo | None:
        async with AsyncNetwork() as network:
            return await network.wait_for_new_device(max_search_duration_seconds)

    device = asyncio.run(_discover())
    return None if device is None else Device.from_discovered_device(device)
