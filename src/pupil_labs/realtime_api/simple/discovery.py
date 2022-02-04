import asyncio
import logging
import typing as T

from ..discovery import Network as AsyncNetwork
from .device import Device

logger = logging.getLogger(__name__)


def discover_devices(search_duration_seconds: float) -> T.List[Device]:
    """Return all devices that could be found in the given search duration.

    .. seealso::
        The asynchronous equivalent
        :py:func:`pupil_labs.realtime_api.discovery.discover_devices`
    """

    async def _discover():
        async with AsyncNetwork() as network:
            await asyncio.sleep(search_duration_seconds)
            return network.devices

    return [Device.from_discovered_device(dev) for dev in asyncio.run(_discover())]


def discover_one_device(
    max_search_duration_seconds: T.Optional[float],
) -> T.Optional[Device]:
    """Return the first device that could be found in the given search duration.

    .. seealso::
        The asynchronous equivalent
        :py:func:`pupil_labs.realtime_api.discovery.Network.wait_for_new_device`
    """

    async def _discover():
        async with AsyncNetwork() as network:
            return await network.wait_for_new_device(timeout_seconds)

    device = asyncio.run(_discover())
    return None if device is None else Device.from_discovered_device(device)
