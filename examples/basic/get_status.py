from pupil_labs.realtime_api.basic import discover_one_device

import logging

# logging.basicConfig(level=logging.DEBUG)

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print(f"Phone IP address: {device.phone_ip}")
print(f"Phone name: {device.phone_name}")
print(f"Phone unique ID: {device.phone_id}")

print(f"Battery level: {device.battery_level_percent}%")
print(f"Battery state: {device.battery_state}")

print(f"Free storage: {device.memory_num_free_bytes / 1024**3}GB")
print(f"Storage level: {device.memory_state}")

print(f"Connected glasses: SN {device.serial_number_glasses}")
print(f"Connected scene camera: SN {device.serial_number_scene_cam}")

world = device.world_sensor()
print(f"World sensor: connected={world.connected} url={world.url}")

gaze = device.gaze_sensor()
print(f"Gaze sensor: connected={gaze.connected} url={gaze.url}")

input(
    "(Dis)connect the device, wait for a few seconds, and press <Enter> "
    "to see the updated status"
)

world = device.world_sensor()
print(f"World sensor: connected={world.connected} url={world.url}")

gaze = device.gaze_sensor()
print(f"Gaze sensor: connected={gaze.connected} url={gaze.url}")

device.close()  # explicitly stop auto-update
