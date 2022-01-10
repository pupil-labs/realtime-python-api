from pupil_labs.realtime_api.simple import discover_one_device, discovered_devices

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...\n\t", end="")
print(discover_one_device(max_search_duration_seconds=10.0))

# List all devices that could be found within 10 seconds
print("Starting 10 second search...\n\t", end="")
print(discovered_devices(search_duration_seconds=10.0))
