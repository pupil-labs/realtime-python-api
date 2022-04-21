import asyncio
import contextlib
import csv
import time

from pupil_labs.realtime_api import Device, Network, receive_gaze_data


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()
        sensor_gaze = status.direct_gaze_sensor()
        if not sensor_gaze.connected:
            print(f"Gaze sensor is not connected to {device}")
            return

        await device.recording_start()
        with open("received_gaze.csv", "w") as fh:
            writer = csv.writer(fh)
            writer.writerow(("ts_gaze", "ts_received"))
            data = []

            restart_on_disconnect = True
            try:
                print("Start writing...")
                async for gaze in receive_gaze_data(
                    sensor_gaze.url, run_loop=restart_on_disconnect
                ):
                    ts = time.perf_counter()
                    data.append((gaze.timestamp_unix_seconds, ts))
            except KeyboardInterrupt:
                pass
            finally:
                await device.recording_stop_and_save()
                writer.writerows(data)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
