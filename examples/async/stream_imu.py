import asyncio
import contextlib

from pupil_labs.realtime_api import Device, Network, receive_imu_data


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()
        sensor_imu = status.direct_imu_sensor()
        if not sensor_imu.connected:
            print(f"Imu sensor is not connected to {device}")
            return

        restart_on_disconnect = True
        async for imu_pack in receive_imu_data(
            sensor_imu.url, run_loop=restart_on_disconnect
        ):
            print(imu_pack)

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
