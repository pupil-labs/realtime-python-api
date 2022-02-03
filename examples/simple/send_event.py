import time

from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print(device.send_event("test event"))

# send event with current timestamp
print(device.send_event("test event", event_timestamp_unix_ns=time.time_ns()))

device.close()
