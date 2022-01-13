import asyncio
import logging

from pupil_labs.realtime_api import Device, StatusUpdateNotifier


def print_component(component):
    print(component)


async def main():
    async with Device("pi.local", 8080) as device:
        print("Starting auto-update")
        # callbacks can be awaitable, too
        notifier = StatusUpdateNotifier(device, callbacks=[print_component])
        await notifier.receive_updates_start()
        await asyncio.sleep(20.0)
        print("Stopping auto-update")
        await notifier.receive_updates_stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
