## Start a Recording

You can remotely control your device, similarly to the Monitor App.

```py linenums="0" title="start_stop_recordings.py"
--8<-- "examples/simple/start_stop_recordings.py:12:13"
```

With a recording ongoing,

## Send event

An event without an explicit timestamp, will be timestamped on arrival at the Neon / Pupil
Invisible Companion device.

=== "Timestamped on Arrival (Host/Companion Device)"

    ```py linenums="0" title="send_event.py"
    --8<-- "examples/simple/send_event.py:12:12"
    ```

=== "With Explicit Timestamp"

    ```py linenums="0" title="send_event.py"
    --8<-- "examples/simple/send_event.py:14:19"
    ```

=== "With Manual Clock Offset Correction"

    ```py linenums="0" title="send_event.py"
    --8<-- "examples/simple/send_event.py:22:36"
    ```

### Check for Errors

```py linenums="0" title="start_stop_recordings.py"
--8<-- "examples/simple/start_stop_recordings.py:16:20"
```

## Stop & Save a Recording

```pyt linenums="0" title="start_stop_recordings.py"
--8<-- "examples/simple/start_stop_recordings.py:24:24"
```

## Cancel a Recording

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
