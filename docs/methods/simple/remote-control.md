You can remotely control your [device][pupil_labs.realtime_api.simple.Device], similarly to the [Monitor App](https://docs.pupil-labs.com/neon/data-collection/monitor-app/) and start, stop, save and annotate recordings.

## Start a Recording

Use [`device.recording_start`][pupil_labs.realtime_api.simple.Device.recording_start] to start a recording on the device and return the recording ID.

```py linenums="0" title="start_stop_recordings.py"
--8<-- "examples/simple/start_stop_recordings.py:12:13"
```

```linenums="0"
Started recording with id 54e7d0bb-5b4c-40e6-baed-f2e11eb4f53b
```

With a recording ongoing, you can:

## Send event

Save [events](https://docs.pupil-labs.com/neon/data-collection/events/) using the [`device.send_event`][pupil_labs.realtime_api.simple.Device.send_event] method. By default, the Neon device receiving the event will assign a timestamp to it, using the time of arrival. Optionally, you can set a custom nanosecond timestamp for your event instead.

=== "Timestamped on Arrival (Host/Companion Device)"

    ```py linenums="0" title="send_event.py"
    --8<-- "examples/simple/send_event.py:12:12"
    ```
    ```py linenums="0"
    Event(name=None recording_id=None timestamp_unix_ns=1744271292116000000 datetime=2025-04-10 09:48:12.116000)
    ```

=== "With Explicit Timestamp"

    ```py linenums="0" title="send_event.py"
    --8<-- "examples/simple/send_event.py:14:19"
    ```
    ```py linenums="0"
    Event(name=None recording_id=None timestamp_unix_ns=1744271291692745000 datetime=2025-04-10 09:48:11.692745)
    ```

=== "With Manual Clock Offset Correction"

    ```py linenums="0" title="send_event.py"
    --8<-- "examples/simple/send_event.py:22:36"
    ```
    ```py linenums="0"
    Clock offset: -437_790_000 ns
    Event(name=None recording_id=None timestamp_unix_ns=1744271293119536000 datetime=2025-04-10 09:48:13.119536)
    ```

Events will **only** be saved if the recording is running. If you send an event while there is no recording, it will be discarded.

!!! info "Event's name"

    Even though the returned `Event.name` is None, the name is being acknowledged by the device.
    TODO:  Ask if we want to return it even though is not being returned in the response.

### Check for Errors

<!-- badge:product Neon -->
<!-- badge:companion +2.9.0 -->
<!-- badge:version +1.5.0 -->

Errors can happen, but now you can also monitor them remotely, by adding the [`device.get_errors`][pupil_labs.realtime_api.simple.Device.get_errors] method on your code, you can get notified of errors (if they happen) during your recording.

```py linenums="0" title="start_stop_recordings.py"
--8<-- "examples/simple/start_stop_recordings.py:16:20"
```

```linenums="0"
Error: Recording Watchdog failure
```

## Stop & Save a Recording

Likewise you can stop and save a recording using [`device.recording_stop_and_save`][pupil_labs.realtime_api.simple.Device.recording_stop_and_save]. Note that if you have a mandatory question that is not filled, the recording will not be saved until that question is answered.

```py linenums="0" title="start_stop_recordings.py"
--8<-- "examples/simple/start_stop_recordings.py:24:24"
```

```linenums="0"
Recording stopped and saved
```

## Cancel a Recording

You can also cancel ([`device.recording_cancel`][pupil_labs.realtime_api.simple.Device.recording_cancel]) a recording if you don't want to save it. This will delete the recording and all its data.

```py linenums="0" title="start_stop_recordings.py"
device.recording_cancel()
```

## Full Code Examples

??? example "Check the whole example code here"

    ```py title="start_stop_recordings.py" linenums="1"
    --8<-- "examples/simple/start_stop_recordings.py"
    ```

    ```py title="send_event.py" linenums="1"
    --8<-- "examples/simple/send_event.py"
    ```
