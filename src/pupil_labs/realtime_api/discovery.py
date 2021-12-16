import asyncio
import contextlib
import functools
import logging
import typing as T

from zeroconf import ServiceStateChange
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceBrowser, AsyncServiceInfo

from .models import DiscoveredDevice

logger = logging.getLogger(__name__)


async def discover_devices() -> T.Iterator[DiscoveredDevice]:
    """Use Bonjour to find devices in the local network that serve the Realtime API."""
    logger.info("Searching for devices...")
    async with AsyncZeroconf() as aiozeroconf:
        queue = asyncio.Queue()
        queue_fn = functools.partial(_queue_service_state_changes, queue)

        browser = AsyncServiceBrowser(
            aiozeroconf.zeroconf, "_http._tcp.local.", handlers=[queue_fn]
        )
        try:
            while True:
                yield await queue.get()
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
    device = DiscoveredDevice(
        name,
        info.server,
        info.port,
        ['.'.join([str(symbol) for symbol in addr]) for addr in info.addresses],
    )
    await queue.put(device)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def print_discovered_devices():
        async for device in discover_devices():
            print(device)

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(print_discovered_devices())
