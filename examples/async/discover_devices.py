import asyncio
import contextlib
import logging

from pupil_labs.realtime_api.discovery import discover_devices


async def main():
    async for device_info in discover_devices():
        print(device_info)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
