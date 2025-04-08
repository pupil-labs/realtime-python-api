You can find one or multiple devices connected to the network.

=== "Discover One Device"

    ```py title="discover_devices.py" linenums="0" hl_lines="4"
    --8<-- "examples/simple/discover_devices.py:1:2,4:5"
    ```

=== "Discover Multiple Devices"

    ```py title="discover_devices.py" linenums="0" hl_lines="4"
    --8<-- "examples/simple/discover_devices.py:1:2,8:9"
    ```

## Device Information

With the device connected, you can access the following device's information:

The [`Device`](../../../api/simple/#pupil_labs.realtime_api.simple.Device) class provides the following attributes:

<!-- TODO: Here following google docstring show the attributes of the `Device` class: -->

Which we can access for example like this:

=== "Get Status"

    ```python title="get_status.py" linenums="0"
    --8<-- "examples/simple/get_status.py"
    ```
    ```title="Output" linenums="0"
    Phone IP address: 192.168.1.168
    Phone name: OnePlus8
    Battery level: 43%
    Free storage: 92.4 GB
    Serial number of connected glasses: h4gcf
    ```

=== "Status Auto-Update"

    ```python linenums="0"
    --8<-- "examples/simple/status_auto_update.py"
    ```

### Automatic status updates

The `Device` class monitors a Neon / Pupil Invisible Companion device in the background and mirrors its state accordingly.

```python linenums="1"
--8<-- "examples/simple/status_auto_update.py"
```

Refer to the [Device API documentation](::: pupil_labs.realtime_api.simple.Device) for more details.

## Full Code Examples

??? example "Check the whole example code here"

    ```py title="discover_devices.py" linenums="1"
    --8<-- "examples/simple/discover_devices.py"
    ```
