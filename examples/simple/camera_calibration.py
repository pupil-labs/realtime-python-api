from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# Device status is fetched on initialization and kept up-to-date in the background

calibration = device.get_calibration()

print("Scene camera matrix:")
print(calibration["scene_camera_matrix"][0])
print("\nScene distortion coefficients:")
print(calibration["scene_distortion_coefficients"][0])

print("\nRight camera matrix:")
print(calibration["right_camera_matrix"][0])
print("\nRight distortion coefficients:")
print(calibration["right_distortion_coefficients"][0])

print("\nLeft camera matrix:")
print(calibration["left_camera_matrix"][0])
print("\nLeft distortion coefficients:")
print(calibration["left_distortion_coefficients"][0])

device.close()
