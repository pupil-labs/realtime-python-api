# Connect to a Device

You can find one or multiple devices connected to your local network and connect to them using:

=== "Discover One Device"

    Using the [`discover_one_device()`][pupil_labs.realtime_api.simple.discover_one_device]:

    ```py title="discover_devices.py" linenums="0" hl_lines="4"
    --8<-- "examples/simple/discover_devices.py:1:2,4:5"
    ```

=== "Discover Multiple Devices"

    Using the [`discover_devices()`][pupil_labs.realtime_api.simple.discover_devices]:

    ```py title="discover_devices.py" linenums="0" hl_lines="4"
    --8<-- "examples/simple/discover_devices.py:1:2,8:9"
    ```

=== "Connect Directly via IP Address"

    ```py linenums="0" hl_lines="4-5"
    from pupil_labs.realtime_api.simple import Device

    # This address is just an example. Find out the actual IP address of your device!
    ip = "192.168.1.169"
    device = Device(address=ip, port="8080")
    ```

Make sure the Companion App is running! If no device can be found, please have a look at the [troubleshooting section](../../troubleshooting.md).

??? quote "Device"

    ::: pupil_labs.realtime_api.simple.Device

## Device Information & Automatic Status Updates

Once connected, the [`Device`][pupil_labs.realtime_api.simple.Device] object provides access to various properties of the Companion Device or glasses, such as [battery level][pupil_labs.realtime_api.simple.Device.battery_level_percent], [free storage][pupil_labs.realtime_api.simple.Device.memory_num_free_bytes], or the [serial numbers][pupil_labs.realtime_api.simple.Device.module_serial] of connected components.

This class, will automatically monitor Neon / Pupil Invisible Companion's Device in the background and mirror its state accordingly.

=== "Get Status"

    ```python title="get_status.py" linenums="0"
    --8<-- "examples/simple/get_status.py"
    ```
    ```py title="Output" linenums="0"
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

    ```title="Output" linenums="0"
    Looking for the next best device...
    Scene camera connected: True
    (Dis)connect the scene camera and hit enter...
    Scene camera connected: False
    ```

Refer to the [Device API documentation](::: pupil_labs.realtime_api.simple.Device) for more details.

## Full Code Examples

??? example "Check the whole example code here"

    ```py title="discover_devices.py" linenums="1"
    --8<-- "examples/simple/discover_devices.py"
    ```
