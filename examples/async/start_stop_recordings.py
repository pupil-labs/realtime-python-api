import asyncio

from pupil_labs.realtime_api import Device, StatusUpdateNotifier, Network
from pupil_labs.realtime_api.models import Recording


async def print_recording(component):
    if isinstance(component, Recording):
        print(f"Update: {component.message}")


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        # get update when recording is fully started
        notifier = StatusUpdateNotifier(device, callbacks=[print_recording])
        await notifier.receive_updates_start()
        recording_id = await device.recording_start()
        print(f"Initiated recording with id {recording_id}")
        await asyncio.sleep(5)
        print("Stopping recording")
        await device.recording_stop_and_save()
        # await control.recording_cancel()  # uncomment to cancel recording
        await asyncio.sleep(2)  # wait for confirmation via auto-update
        await notifier.receive_updates_stop()


if __name__ == "__main__":
    asyncio.run(main())
