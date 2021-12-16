import asyncio
import logging
import time

from pupil_labs.realtime_api import Control


async def main():
    async with Control("pi.local", 8080) as control:
        # send event without timestamp
        print(await control.send_event("test event"))

        # send event with current timestamp
        print(
            await control.send_event(
                "test event", event_timestamp_unix_ns=time.time_ns()
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
