import asyncio
import contextlib

from pupil_labs.realtime_api import Device, discover_one_device, receive_gaze_data


async def main():
    dev_info = await discover_one_device(max_search_duration_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()
        sensor_gaze = status.direct_gaze_sensor()
        if not sensor_gaze.connected:
            print(f"Gaze sensor is not connected to {device}")
            return

        restart_on_disconnect = True
        async for gaze in receive_gaze_data(
            sensor_gaze.url, run_loop=restart_on_disconnect
        ):
            print(gaze)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
