from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# Device status is fetched on initialization and kept up-to-date in the background

print(f"Phone IP address: {device.phone_ip}")
print(f"Phone name: {device.phone_name}")
print(f"Phone unique ID: {device.phone_id}")

print(f"Battery level: {device.battery_level_percent}%")
print(f"Battery state: {device.battery_state}")

print(f"Free storage: {device.memory_num_free_bytes / 1024**3}GB")
print(f"Storage level: {device.memory_state}")

print(f"Connected glasses: SN {device.serial_number_glasses}")
print(f"Connected scene camera: SN {device.serial_number_scene_cam}")

device.close()  # explicitly stop auto-update
