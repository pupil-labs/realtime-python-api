import asyncio
import logging

from pupil_labs.realtime_api import Device


async def print_component(component):
    print(component)


async def main():
    async with Device("pi.local", 8080) as device:
        print("Starting auto-update")
        await device.start_auto_update(update_callback=print_component)
        await asyncio.sleep(20.0)
        print("Stopping auto-update")
        await device.stop_auto_update()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
