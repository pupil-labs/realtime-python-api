from pupil_labs.realtime_api.simple import Network

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = Network().wait_for_new_device(timeout_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# device.streaming_start()  # optional, if not called, stream is started on-demand

try:
    while True:
        print(device.receive_gaze_datum())
except KeyboardInterrupt:
    pass
finally:
    print("Stopping...")
    # device.streaming_stop()  # optional, if not called, stream is stopped on close
    device.close()  # explicitly stop auto-update
