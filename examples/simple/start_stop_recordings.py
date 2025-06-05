import time

from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print("Starting recording")
recording_id = device.recording_start()
print(f"Started recording with id {recording_id}")

# Check for errors while recording runs
start_time = time.time()
while time.time() - start_time < 5:
    for e in device.get_errors():
        print("Error:", e)

    time.sleep(1)

device.recording_stop_and_save()

print("Recording stopped and saved")
# device.recording_cancel()  # uncomment to cancel recording

device.close()
