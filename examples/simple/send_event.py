import time

from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print(device.send_event("test event; timestamped at arrival"))

# send event with current timestamp
print(
    device.send_event(
        "test event; timestamped by the client, relying on NTP for sync",
        event_timestamp_unix_ns=time.time_ns(),
    )
)

# Estimate clock offset between Companion device and client script
# (only needs to be done once)
estimate = device.estimate_time_offset()
clock_offset_ns = round(estimate.time_offset_ms.mean * 1_000_000)
print(f"Clock offset: {clock_offset_ns:_d} ns")

# send event with current timestamp, but correct it manual for possible clock offset
current_time_ns_in_client_clock = time.time_ns()
current_time_ns_in_companion_clock = current_time_ns_in_client_clock - clock_offset_ns
print(
    device.send_event(
        "test event; timestamped by the client, manual clock offset correction",
        event_timestamp_unix_ns=current_time_ns_in_companion_clock,
    )
)


device.close()
