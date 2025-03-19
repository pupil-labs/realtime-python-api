import asyncio
import contextlib
from datetime import datetime, timezone

from pupil_labs.realtime_api import Device, Network, receive_eye_events_data
from pupil_labs.realtime_api.streaming.eye_events import (
    BlinkEventData,
    FixationEventData,
)


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
            if isinstance(eye_event, BlinkEventData):
                print(
                    "[BLINK] blinked at "
                    f"{
                        datetime.fromtimestamp(
                            eye_event.start_time_ns // 1e9, timezone.utc
                        ).strftime('%H:%M:%S')
                    } UTC"
                )
            elif isinstance(eye_event, FixationEventData) and eye_event.event_type == 0:
                print(
                    f"[SACCADE] event with {eye_event.amplitude_angle_deg:.0f}° amplitude."
                )
            elif isinstance(eye_event, FixationEventData) and eye_event.event_type == 1:
                print(
                    "[FIXATION] event with duration of "
                    f"{(eye_event.end_time_ns - eye_event.start_time_ns) / 1e9:.2f} seconds."
                )
            # print(eye_event) # This will print all the fields of the eye event


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
