import csv
import time

from pupil_labs.realtime_api.simple import discover_one_device

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# device.streaming_start()  # optional, if not called, stream is started on-demand

device.recording_start()
with open("received_gaze.csv", "w") as fh:
    writer = csv.writer(fh)
    writer.writerow(("ts_gaze", "ts_received"))
    data = []
    try:
        print(f"Start recording from {device.phone_name}...")
        start = time.perf_counter()
        count = 0
        while True:
            gaze = device.receive_gaze_datum()
            ts = time.perf_counter()
            data.append((gaze.timestamp_unix_seconds, ts))
            count += 1
            time_since_start = ts - start
            if time_since_start > 10:
                print(f" Front: {count} counted @ {count/time_since_start:.2f} Hz")
                start = ts
                count = 0

    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping...")
        device.recording_stop_and_save()
        # device.streaming_stop()  # optional, if not called, stream is stopped on close
        device.close()  # explicitly stop auto-update
        writer.writerows(data)
