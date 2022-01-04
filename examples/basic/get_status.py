from pupil_labs.realtime_api.basic import discover_one_device

import logging

logging.basicConfig(level=logging.DEBUG)

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print(f"Device IP address: {device._status.phone.ip}")
print(f"Battery level: {device._status.phone.battery_level} %")

print(f"Connected glasses: SN {device._status.hardware.glasses_serial}")
print(f"Connected scene camera: SN {device._status.hardware.world_camera_serial}")

world = device._status.direct_world_sensor()
print(f"World sensor: connected={world.connected} url={world.url}")

gaze = device._status.direct_gaze_sensor()
print(f"Gaze sensor: connected={gaze.connected} url={gaze.url}")

device.close()  # explicitly stop auto-update
