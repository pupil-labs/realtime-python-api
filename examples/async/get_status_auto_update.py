import asyncio
import logging

from pupil_labs.realtime_api import Device


def print_component(component):
    print(component)


async def async_callback_example(component):
    await asyncio.sleep(0.1)


async def main():
    async with Device("pi.local", 8080) as device:
        print("Starting auto-update")
        await device.auto_update_start(
            update_callback=print_component,
            update_callback_async=async_callback_example,
        )
        await asyncio.sleep(20.0)
        print("Stopping auto-update")
        await device.auto_update_stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
