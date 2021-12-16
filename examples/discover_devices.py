import asyncio
import contextlib
import logging

from pupil_labs.realtime_api.discovery import discover_devices


async def main():
    async for device in discover_devices():
        print(device)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
