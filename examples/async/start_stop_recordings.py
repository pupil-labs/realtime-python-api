import asyncio
import logging

from pupil_labs.realtime_api import Device, StatusUpdateNotifier
from pupil_labs.realtime_api.models import Recording


async def print_recording(component):
    if isinstance(component, Recording):
        print(f"Update: {component.message}")


async def main():
    async with Device("pi.local", 8080) as device:
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
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
