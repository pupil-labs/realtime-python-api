import asyncio

from pupil_labs.realtime_api import Device, Network


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()

        print(f"Device IP address: {status.phone.ip}")
        print(f"Battery level: {status.phone.battery_level} %")

        print(f"Connected glasses: SN {status.hardware.glasses_serial}")
        print(f"Connected scene camera: SN {status.hardware.world_camera_serial}")

        world = status.direct_world_sensor()
        print(f"World sensor: connected={world.connected} url={world.url}")

        gaze = status.direct_gaze_sensor()
        print(f"Gaze sensor: connected={gaze.connected} url={gaze.url}")


if __name__ == "__main__":
    asyncio.run(main())
