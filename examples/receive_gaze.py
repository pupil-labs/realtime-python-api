import asyncio
import logging

from pupil_labs.realtime_api import Control, receive_gaze_data


async def main():
    async with Control("pi.local", 8080) as control:
        status = await control.get_status()
        sensor_gaze = status.direct_gaze_sensor()
        if not sensor_gaze.connected:
            logging.error(f"Gaze sensor is not connected to {control}")
            return

        async for gaze in receive_gaze_data(sensor_gaze.url):
            print(gaze)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
