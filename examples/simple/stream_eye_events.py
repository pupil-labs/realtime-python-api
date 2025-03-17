from datetime.datetime import utcfromtimestamp

from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.realtime_api.streaming.eye_events import (
    BlinkEventData,
    FixationEventData,
)

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# device.streaming_start()  # optional, if not called, stream is started on-demand

try:
    while True:
        event = device.receive_eye_events()
        if isinstance(event, BlinkEventData):
            print(f"Blink event at {utcfromtimestamp(event.start_time_ns / 1e9)}")
        elif isinstance(event, FixationEventData) and event.event_type == 0:
            print(f"Saccade event with {event.max_velocity} px/sec max velocity.")
        elif isinstance(event, FixationEventData) and event.event_type == 1:
            print(
                "Fixation event with duration of "
                f"{(event.start_time_ns - event.end_time_ns) / 1e9} seconds."
            )
except KeyboardInterrupt:
    pass
finally:
    print("Stopping...")
    # device.streaming_stop()  # optional, if not called, stream is stopped on close
    device.close()  # explicitly stop auto-update
