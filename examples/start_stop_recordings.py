import asyncio
import logging

from pupil_labs.realtime_api import Control


async def main():
    async with Control("pi.local", 8080) as control:
        recording_id = await control.recording_start()
        print(f"Started recording with id {recording_id}")
        await asyncio.sleep(5)
        await control.recording_stop_and_save()
        print("Recording stopped and saved")
        # await control.recording_cancel()  # uncomment to cancel recording


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
