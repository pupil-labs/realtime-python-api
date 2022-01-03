import asyncio
import contextlib
import logging

from pupil_labs.realtime_api import Device, receive_gaze_data


async def main():
    async with Device("pi.local", 8080) as device:
        status = await device.get_status()
        sensor_gaze = status.direct_gaze_sensor()
        if not sensor_gaze.connected:
            logging.error(f"Gaze sensor is not connected to {device}")
            return

        restart_on_disconnect = True
        async for gaze in receive_gaze_data(
            sensor_gaze.url, run_loop=restart_on_disconnect
        ):
            print(gaze)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
