import time

from pupil_labs.realtime_api.simple import Network

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = Network().wait_for_new_device(timeout_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

print(f"Starting recording")
recording_id = device.recording_start()
print(f"Started recording with id {recording_id}")

time.sleep(5)

device.recording_stop_and_save()

print("Recording stopped and saved")
# device.recording_cancel()  # uncomment to cancel recording

device.close()
