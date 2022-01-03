import asyncio
import functools
import logging
import time
import typing as T

from zeroconf import ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from .models import DiscoveredDeviceInfo

logger = logging.getLogger(__name__)


async def discover_devices(
    timeout_seconds: T.Optional[float] = None,
) -> T.AsyncIterator[DiscoveredDeviceInfo]:
    """Use Bonjour to find devices in the local network that serve the Realtime API.

    :param timeout_seconds: Stop after ``timeout_seconds``. If ``None``, run discovery
        forever.
    """
    logger.info("Searching for devices...")
    async with AsyncZeroconf() as aiozeroconf:
        queue = asyncio.Queue()
        queue_fn = functools.partial(_queue_service_state_changes, queue)

        browser = AsyncServiceBrowser(
            aiozeroconf.zeroconf, "_http._tcp.local.", handlers=[queue_fn]
        )
        try:
            while True:
                if timeout_seconds <= 0.0:
                    return
                try:
                    t0 = time.perf_counter()
                    yield await asyncio.wait_for(queue.get(), timeout=timeout_seconds)
                    if timeout_seconds is not None:
                        timeout_seconds -= time.perf_counter() - t0
                except asyncio.TimeoutError:
                    return
        finally:
            await browser.async_cancel()


def is_valid_service_name(name: str) -> bool:
    return name.split(":")[0] == "PI monitor"


def _queue_service_state_changes(
    queue, zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    if is_valid_service_name(name) and state_change == ServiceStateChange.Added:
        asyncio.create_task(
            _request_info_for_valid_services_and_queue_result(
                queue, zeroconf, service_type, name, timeout_ms=3000
            )
        )


async def _request_info_for_valid_services_and_queue_result(
    queue, zeroconf, service_type, name, timeout_ms
):
    info = AsyncServiceInfo(service_type, name)
    await info.async_request(zeroconf, timeout_ms)
    device = DiscoveredDeviceInfo(
        name,
        info.server,
        info.port,
        ['.'.join([str(symbol) for symbol in addr]) for addr in info.addresses],
    )
    await queue.put(device)
