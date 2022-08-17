import asyncio

from pupil_labs.realtime_api import Device, Network
from pupil_labs.realtime_api.time_echo import TimeOffsetEstimator


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()

        print(f"Device IP address: {status.phone.ip}")
        print(f"Device Time Echo port: {status.phone.time_echo_port}")

        if status.phone.time_echo_port is None:
            print(
                "You Pupil Invisible Companion app is out-of-date and does not yet "
                "support the Time Echo protocol. Upgrade to version 1.4.28 or newer."
            )
            return

        time_offset_estimator = TimeOffsetEstimator(
            status.phone.ip, status.phone.time_echo_port
        )
        estimated_offset = await time_offset_estimator.estimate()
        print(f"Mean time offset: {estimated_offset.time_offset_ms.mean} ms")
        print(
            "Mean roundtrip duration: "
            f"{estimated_offset.roundtrip_duration_ms.mean} ms"
        )


if __name__ == "__main__":
    asyncio.run(main())
