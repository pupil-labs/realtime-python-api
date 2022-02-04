import asyncio

from pupil_labs.realtime_api import Device, StatusUpdateNotifier, Network


def print_component(component):
    print(component)


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        duration = 20
        print(f"Starting auto-update for {duration} seconds")
        # callbacks can be awaitable, too
        notifier = StatusUpdateNotifier(device, callbacks=[print_component])
        await notifier.receive_updates_start()
        await asyncio.sleep(duration)
        print("Stopping auto-update")
        await notifier.receive_updates_stop()


if __name__ == "__main__":
    asyncio.run(main())
