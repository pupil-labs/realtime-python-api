import asyncio
import contextlib

from pupil_labs.realtime_api import Device, discover_one_device


async def main():
    dev_info = await discover_one_device(max_search_duration_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        print("Waiting for status updates... hit ctrl-c to stop.")
        async for changed in device.status_updates():
            print(changed)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
