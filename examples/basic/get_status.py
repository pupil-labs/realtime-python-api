from pupil_labs.realtime_api.basic import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print("Getting status...")
status = device.get_status()

print(f"Device IP address: {status.phone.ip}")
print(f"Battery level: {status.phone.battery_level} %")

print(f"Connected glasses: SN {status.hardware.glasses_serial}")
print(f"Connected scene camera: SN {status.hardware.world_camera_serial}")

world = status.direct_world_sensor()
print(f"World sensor: connected={world.connected} url={world.url}")

gaze = status.direct_gaze_sensor()
print(f"Gaze sensor: connected={gaze.connected} url={gaze.url}")
