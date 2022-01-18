import asyncio
import time

from pupil_labs.realtime_api import Device, discover_one_device


async def main():
    dev_info = await discover_one_device(max_search_duration_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        # send event without timestamp
        print(await device.send_event("test event"))

        # send event with current timestamp
        print(
            await device.send_event(
                "test event", event_timestamp_unix_ns=time.time_ns()
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
