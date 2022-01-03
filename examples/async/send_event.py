import asyncio
import logging
import time

from pupil_labs.realtime_api import Device


async def main():
    async with Device("pi.local", 8080) as device:
        # send event without timestamp
        print(await device.send_event("test event"))

        # send event with current timestamp
        print(
            await device.send_event(
                "test event", event_timestamp_unix_ns=time.time_ns()
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
