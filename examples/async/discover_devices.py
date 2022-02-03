import asyncio
import contextlib

from pupil_labs.realtime_api.discovery import Network, discover_devices


async def main():
    async with Network() as network:
        print("Looking for the next best device...\n\t", end="")
        print(await network.wait_for_new_device(timeout_seconds=5))

        print("---")
        print("All devices after searching for additional 5 seconds:")
        await asyncio.sleep(5)
        print(network.devices)

    print("---")
    print("Starting new, indefinitive search... hit ctrl-c to stop.")
    # optionally set timeout_seconds argument to limit search duration
    async for device_info in discover_devices():
        print(f"\t{device_info}")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
