import asyncio
import logging

from pupil_labs.realtime_api import Device, Network, discover_devices


async def main():
    dev_info = None
    async for dev_info in discover_devices():
        if "9865e04c385bcb59" in dev_info.name:
            break

    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device._camera_control(
            ae_mode="auto", man_exp=50, gain=50, brightness=0, contrast=70, gamma=300
        )
        print(status)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    asyncio.run(main())
