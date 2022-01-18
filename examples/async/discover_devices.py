import asyncio
import contextlib

from pupil_labs.realtime_api.discovery import discover_devices, discover_one_device


async def main():
    print("Looking for the next best device...\n\t", end="")
    print(await discover_one_device(max_search_duration_seconds=5))

    print("Starting new, indefinitive search... hit ctrl-c to stop.")
    # optionally set timeout_seconds argument to limit search duration
    async for device_info in discover_devices():
        print(f"\t{device_info}")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
