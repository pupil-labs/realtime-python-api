import asyncio
import contextlib
import logging

from pupil_labs.realtime_api import Device


async def main():
    async with Device("pi.local", 8080) as device:
        print("Waiting for status updates... hit ctrl-c to stop.")
        async for changed in device.status_updates():
            print(changed)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
