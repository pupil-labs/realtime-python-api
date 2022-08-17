from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    raise SystemExit("No device found.")

estimate = device.estimate_time_offset()
if estimate is None:
    device.close()
    raise SystemExit("Pupil Companion app is too old")

print(f"Mean time offset: {estimate.time_offset_ms.mean} ms")
print(f"Mean roundtrip duration: {estimate.roundtrip_duration_ms.mean} ms")

device.close()
