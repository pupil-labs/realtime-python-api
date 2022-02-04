import asyncio
import time

from pupil_labs.realtime_api import Device, Network


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
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
