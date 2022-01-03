import asyncio
import logging

from pupil_labs.realtime_api import Device


async def main():
    async with Device("pi.local", 8080) as control:
        status = await control.get_status()

        print(f"Device IP address: {status.phone.ip}")
        print(f"Battery level: {status.phone.battery_level} %")

        print(f"Connected glasses: SN {status.hardware.glasses_serial}")
        print(f"Connected scene camera: SN {status.hardware.world_camera_serial}")

        world = status.direct_world_sensor()
        print(f"World sensor: connected={world.connected} url={world.url}")

        gaze = status.direct_gaze_sensor()
        print(f"Gaze sensor: connected={gaze.connected} url={gaze.url}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
