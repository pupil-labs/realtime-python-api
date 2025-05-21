This module comes in two flavours, [async][pupil_labs.realtime_api] and [simple][pupil_labs.realtime_api.simple]. If you are new to it, we recommend you to start with the `simple` interface. The `async` interface is more flexible and allows for non-blocking communication, but it is also more complex to use.

Here we will show you how to get started with the `simple` interface, which is the recommended way to use the library if you are new to it. If you are already familiar, you can skip this section and go straight to the [methods](./methods/simple.md).

If you are unsure which one to use, scroll down to the end of this page for more information.

## Quick Start

### Connecting to a Device

The first step would be to connect to the device. Using the discover_one_device function, we can connect to a Neon device connected to your local network. Make sure the Neon Companion app is running! If no device can be found, please check the [troubleshooting section](./troubleshooting.md).

```py
from pupil_labs.realtime_api.simple import discover_one_device
device = discover_one_device()
```

With the device connected, you can now access the device's properties:

```py
print(f"Phone IP address: {device.phone_ip}")
print(f"Phone name: {device.phone_name}")
print(f"Battery level: {device.battery_level_percent}%")
print(f"Free storage: {device.memory_num_free_bytes / 1024**3:.1f} GB")
print(f"Serial number of connected glasses: {device.serial_number_glasses}")
```

```
Phone IP address: 192.168.1.168
Phone name: OnePlus8
Battery level: 43%
Free storage: 92.4 GB
Serial number of connected glasses: h4gcf
```

Have a look at the [connect to a device page](./methods/simple/connect-to-a-device.md) for more ways to connect to a device.

### Starting & Stopping a Recording

Use the recording_start and recording_stop_and_save methods to remotely start and stop recordings.

```py
import time
from pupil_labs.realtime_api.simple import discover_one_device

device = discover_one_device()

recording_id = device.recording_start()
print(f"Started recording with id {recording_id}")

time.sleep(5)

device.recording_stop_and_save()
```

```
Started recording with id 2f99d9f9-f009-4015-97dd-eb253de443b0
```

### Sending Events

While a recording is running, you can save events using the send_event method. By default, the device receiving the event will assign a timestamp to it, using the time of arrival. Optionally, you can set a custom nanosecond timestamp for your event instead.

```py
from pupil_labs.realtime_api.simple import discover_one_device
device = discover_one_device()

device.recording_start()

print(device.send_event("test event 1"))

time.sleep(5)

# send event with current timestamp
print(device.send_event("test event 2", event_timestamp_unix_ns=time.time_ns()))

device.recording_stop_and_save()
```

```
Event(name=None recording_id=None timestamp_unix_ns=1642599117043000000 datetime=2022-01-19 14:31:57.043000)
Event(name=None recording_id=fd8c98ca-cd6c-4d3f-9a05-fbdb0ef42668 timestamp_unix_ns=1642599122555200500 datetime=2022-01-19 14:32:02.555201)
```

### Receiving Data

You can receive the current scene camera frame as well as the current gaze sample using the receive_matched_scene_video_frame_and_gaze method. This method can also provide pupil diameter and eye poses and eye openness data, separately for each eye (on Neon). An example is provided below:

```py
import cv2
import matplotlib.pyplot as plt
from pupil_labs.realtime_api.simple import discover_one_device

device = discover_one_device()

scene_sample, gaze_sample = device.receive_matched_scene_video_frame_and_gaze()

print("This sample contains the following data:\n")
print(f"Gaze x and y coordinates: {gaze_sample.x}, {gaze_sample.y}\n")
print(
    f"Pupil diameter in millimeters for the left eye: {gaze_sample.pupil_diameter_left} and the right eye: {gaze_sample.pupil_diameter_right}\n"
)
print(
    "Location of left and right eye ball centers in millimeters in relation to the scene camera of the Neon module."
)
print(
    f"For the left eye x, y, z: {gaze_sample.eyeball_center_left_x}, {gaze_sample.eyeball_center_left_y}, {gaze_sample.eyeball_center_left_z} and for the right eye x, y, z: {gaze_sample.eyeball_center_right_x}, {gaze_sample.eyeball_center_right_y}, {gaze_sample.eyeball_center_right_z}.\n"
)
print("Directional vector describing the optical axis of the left and right eye.")
print(
    f"For the left eye x, y, z: {gaze_sample.optical_axis_left_x}, {gaze_sample.optical_axis_left_y}, {gaze_sample.optical_axis_left_z} and for the right eye x, y, z: {gaze_sample.optical_axis_right_x}, {gaze_sample.optical_axis_right_y}, {gaze_sample.optical_axis_right_z}.\n"
)
print("Angles and aperture describing the eyelid openness of the left and right eye.")
print(
    f"For the left eye upper lid angle, lower lid angle, and aperture: {gaze_sample.eyelid_angle_top_left}, {gaze_sample.eyelid_angle_bottom_left}, {gaze_sample.eyelid_aperture_left} and for the right eye: {gaze_sample.eyelid_angle_top_right}, {gaze_sample.eyelid_angle_bottom_right}, {gaze_sample.eyelid_aperture_right}."
)

scene_image_rgb = cv2.cvtColor(scene_sample.bgr_pixels, cv2.COLOR_BGR2RGB)
plt.imshow(scene_image_rgb)
plt.scatter(gaze_sample.x, gaze_sample.y, s=200, facecolors="none", edgecolors="r")
device.close()
plt.show()
```

The output data would look as follows:

```
This sample contains the following data:

Gaze x and y coordinates: 732.8187255859375, 604.2568359375

Pupil diameter in millimeters for the left eye: 3.873124122619629 and the right eye: 3.441348075866699

Location of left and right eye ball centers in millimeters in relation to the scene camera of the Neon module.
For the left eye x, y, z: -30.625, 14.09375, -33.96875 and for the right eye x, y, z: 32.4375, 14.375, -33.9375.

Directional vector describing the optical axis of the left and right eye.
For the left eye x, y, z: -0.015054119750857353, 0.10672548413276672, 0.9941745400428772 and for the right eye x, y, z: -0.06556398421525955, 0.09701070189476013, 0.9931215047836304.

Angles and aperture describing the eyelid openness of the left and right eye.
For the left eye upper lid angle, lower lid angle, and aperture: 0.39990234375, -0.5849609375, 10.859789848327637 and for the right eye: 0.396484375, -0.609375, 11.100102424621582.
```

Alternatively, you could also use the receive_scene_video_frame and receive_gaze_datum methods to obtain each sample separately. The receive_matched_scene_video_frame_and_gaze method does however also ensure that both samples are matched temporally.

Similarly, you can also receive the IMU data, fixations, saccades or other data streams. Have a look at the [methods](./methods/simple.md) page for more information.

## Simple & Async API

1. The [`async`][pupil_labs.realtime_api] interface is using Python's [asyncio](https://docs.python.org/3/library/asyncio.html) in order to implement non-blocking asynchronous communication.

2. The [`simple`][pupil_labs.realtime_api.simple] interface wraps around the `async` one sacrificing flexibility for the sake of ease of use. The calls made using the simple mode are blocking. If you don't know what any of this means, that's okay! The simple mode suffices for most use-cases and you usually do not need to understand the differences!

To get started with either version, check out our [code examples](./methods/index.md).

If you are still unsure which one to use, and you are familiar with Python's `asyncio`, you can check out the [Simple vs Async guide](./guides/simple-vs-async-api.md) to better understand the differences between the two interfaces.
