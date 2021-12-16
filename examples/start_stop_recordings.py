import asyncio
import logging

from pupil_labs.realtime_api import Control


async def main():
    async with Control("pi.local", 8080) as control:
        await control.start_recording()
        await asyncio.sleep(5)
        await control.stop_and_save_recording()
        # await control.cancel_recording()  # uncomment to cancel recording


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
