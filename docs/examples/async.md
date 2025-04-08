# Asynchronous Examples

!!! note
The examples require Python 3.7+ to run and use the `asyncio` framework.

## Remote Control

### Get Current Status

```python linenums="1" hl_lines="7 8 13 14"
--8<-- "examples/async/device_status_get_current.py"
```

### Status Updates

Wait for status updates from the device

```python linenums="1" hl_lines="16"
--8<-- "examples/async/device_status_update_wait.py"
```

Get a callback when there is a new status updates

```python linenums="1" hl_lines="21 22 25"
--8<-- "examples/async/device_status_update_via_callback.py"
```

### Send Event

An event without an explicit timestamp, will be timestamped on arrival at the Neon / Pupil
Invisible Companion device.

```python linenums="1" hl_lines="16 20 21 22"
--8<-- "examples/async/send_event.py"
```

### Start, stop and save, and cancel recordings

```python linenums="1" hl_lines="23 27"
--8<-- "examples/async/start_stop_recordings.py"
```

### Templates

You can programmatically fill the template. This allows you to also define the
recording name if the template is created correctly.

```python linenums="1" hl_lines="59 61 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 110 113"
--8<-- "examples/async/templates.py"
```

## Streaming

### Gaze Data

```python linenums="1" hl_lines="16 22 23 24"
--8<-- "examples/async/stream_gaze.py"
```

### Scene Camera Video

```python linenums="1" hl_lines="18 24 25 26"
--8<-- "examples/async/stream_scene_camera_video.py"
```

### Eyes Camera Video

```python linenums="1" hl_lines="20 28"
--8<-- "examples/async/stream_eyes_camera_video.py"
```

### Scene Camera Video With Overlayed Gaze

This example processes two streams (video and gaze data) at the same time, matches each
video frame with its temporally closest gaze point, and previews both in a window.

```python linenums="1" hl_lines="43 49 70 71"
--8<-- "examples/async/stream_video_with_overlayed_gaze.py"
```

## Device Discovery

```python linenums="1" hl_lines="8 10 15 20"
--8<-- "examples/async/discover_devices.py"
```

## Time Offset Estimation

See `pupil_labs.realtime_api.time_echo` for details.

```python linenums="1" hl_lines="18 27 28 29 30 31 34"
--8<-- "examples/async/device_time_offset.py"
```

# Asynchronous Examples

!!! note
The examples require Python 3.7+ to run and use the `asyncio` framework.

## Remote Control

### Get Current Status

```python linenums="1" hl_lines="7 8 13 14"
--8<-- "examples/async/device_status_get_current.py"
```

### Status Updates

Wait for status updates from the device

```python linenums="1" hl_lines="16"
--8<-- "examples/async/device_status_update_wait.py"
```

Get a callback when there is a new status updates

```python linenums="1" hl_lines="21 22 25"
--8<-- "examples/async/device_status_update_via_callback.py"
```

### Send Event

An event without an explicit timestamp, will be timestamped on arrival at the Neon / Pupil
Invisible Companion device.

```python linenums="1" hl_lines="16 20 21 22"
--8<-- "examples/async/send_event.py"
```

### Start, stop and save, and cancel recordings

```python linenums="1" hl_lines="23 27"
--8<-- "examples/async/start_stop_recordings.py"
```

### Templates

You can programmatically fill the template. This allows you to also define the
recording name if the template is created correctly.

```python linenums="1" hl_lines="59 61 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 110 113"
--8<-- "examples/async/templates.py"
```

## Streaming

### Gaze Data

```python linenums="1" hl_lines="16 22 23 24"
--8<-- "examples/async/stream_gaze.py"
```

### Scene Camera Video

```python linenums="1" hl_lines="18 24 25 26"
--8<-- "examples/async/stream_scene_camera_video.py"
```

### Eyes Camera Video

```python linenums="1" hl_lines="20 28"
--8<-- "examples/async/stream_eyes_camera_video.py"
```

### Scene Camera Video With Overlayed Gaze

This example processes two streams (video and gaze data) at the same time, matches each
video frame with its temporally closest gaze point, and previews both in a window.

```python linenums="1" hl_lines="43 49 70 71"
--8<-- "examples/async/stream_video_with_overlayed_gaze.py"
```

## Device Discovery

```python linenums="1" hl_lines="8 10 15 20"
--8<-- "examples/async/discover_devices.py"
```

## Time Offset Estimation

See `pupil_labs.realtime_api.time_echo` for details.

```python linenums="1" hl_lines="18 27 28 29 30 31 34"
--8<-- "examples/async/device_time_offset.py"
```
