import asyncio
import contextlib

from pupil_labs.realtime_api import Device, Network, receive_eye_events_data


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()
        sensor_eye_events = status.direct_eye_events_sensor()
        if not sensor_eye_events.connected:
            print(f"Eye events sensor is not connected to {device}")
            return

        restart_on_disconnect = True
        async for eye_event in receive_eye_events_data(
            sensor_eye_events.url, run_loop=restart_on_disconnect
        ):
            print(eye_event)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
