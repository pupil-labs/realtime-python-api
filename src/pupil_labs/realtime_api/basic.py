import asyncio
import threading
import typing as T
import weakref

from .base import DeviceBase
from .device import Device as _DeviceAsync
from .discovery import discover_devices as _discover_devices_async
from .models import DiscoveredDeviceInfo, Event, Sensor, Status


def discovered_devices(search_duration_seconds: float) -> T.List["Device"]:
    """Return all devices that could be found in the given search duration."""

    async def _collect_device_information() -> T.List[DiscoveredDeviceInfo]:
        return [
            dev_info
            async for dev_info in _discover_devices_async(search_duration_seconds)
        ]

    return [
        Device.from_discovered_device(dev_info)
        for dev_info in asyncio.run(_collect_device_information())
    ]


def discover_one_device(
    max_search_duration_seconds: T.Optional[float],
) -> T.Optional["Device"]:
    """Search until one device is found."""

    async def _return_first_device() -> T.Optional[DiscoveredDeviceInfo]:
        async for dev_info in _discover_devices_async(max_search_duration_seconds):
            return dev_info
        return None

    dev_info = asyncio.run(_return_first_device())
    if dev_info is not None:
        return Device.from_discovered_device(dev_info)
    return None


class Device(DeviceBase):
    """
    .. hint::
        Use :py:func:`.discover_one_device` or :py:func:`.discovered_devices` instead of
        initializing the class manually. See the :ref:`basic_discovery_example` example.

    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._status = self._get_status()
        self._should_close_flag: T.Optional[asyncio.Event] = None
        auto_update_started = threading.Event()
        self._auto_update_thread = threading.Thread(
            target=self._auto_update,
            kwargs=dict(
                device_weakref=weakref.ref(self),
                auto_update_started_flag=auto_update_started,
            ),
            name=f"{self} auto-update thread",
        )
        self._auto_update_thread.start()
        auto_update_started.wait()

    def close(self) -> None:
        if self._should_close_flag:
            self._should_close_flag.set()
            self._auto_update_thread.join()

    def __del__(self):
        self.close()

    @property
    def phone_name(self) -> str:
        return self._status.phone.device_name

    @property
    def phone_id(self) -> str:
        return self._status.phone.device_id

    @property
    def phone_ip(self) -> str:
        return self._status.phone.ip

    @property
    def battery_level_percent(self) -> int:
        return self._status.phone.battery_level

    @property
    def battery_state(self) -> T.Literal["OK", "LOW", "CRITICAL"]:
        return self._status.phone.battery_state

    @property
    def memory_num_free_bytes(self) -> int:
        return self._status.phone.memory

    @property
    def memory_state(self) -> T.Literal["OK", "LOW", "CRITICAL"]:
        return self._status.phone.memory_state

    @property
    def version_glasses(self) -> str:
        return self._status.hardware.version

    @property
    def serial_number_glasses(self) -> T.Union[str, None, T.Literal["default"]]:
        """Returns ``None`` or ``"default"`` if no glasses are connected"""
        return self._status.hardware.glasses_serial

    @property
    def serial_number_scene_cam(self) -> T.Optional[str]:
        """Returns ``None`` if no scene camera is connected"""
        return self._status.hardware.world_camera_serial

    def world_sensor(self) -> T.Optional[Sensor]:
        return self._status.direct_world_sensor()

    def gaze_sensor(self) -> T.Optional[Sensor]:
        return self._status.direct_gaze_sensor()

    def recording_start(self) -> str:
        """Wraps :py:meth:`pupil_labs.realtime_api.device.Device.recording_start`

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the recording could not be started. Possible reasons include
            - Recording already running
            - Template has required fields
            - Low battery
            - Low storage
            - No wearer selected
            - No workspace selected
            - Setup bottom sheets not completed
        """

        async def _start_recording():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.recording_start()

        return asyncio.run(_start_recording())

    def recording_stop_and_save(self):
        """Wraps :py:meth:`pupil_labs.realtime_api.device.Device.recording_stop_and_save`

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the recording could not be started
            Possible reasons include
            - Recording not running
            - template has required fields
        """

        async def _stop_and_save_recording():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.recording_stop_and_save()

        return asyncio.run(_stop_and_save_recording())

    def recording_cancel(self):
        """Wraps :py:meth:`pupil_labs.realtime_api.device.Device.recording_cancel`

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the recording could not be started
            Possible reasons include
            - Recording not running
        """

        async def _cancel_recording():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.recording_cancel()

        return asyncio.run(_cancel_recording())

    def send_event(
        self, event_name: str, event_timestamp_unix_ns: T.Optional[int] = None
    ) -> Event:
        """
        :raises pupil_labs.realtime_api.device.DeviceError: if sending the event fails
        """

        async def _send_event():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.send_event(event_name, event_timestamp_unix_ns)

        return asyncio.run(_send_event())

    def _get_status(self) -> Status:
        """Request the device's current status.

        Wraps :py:meth:`pupil_labs.realtime_api.device.Device.get_status`

        :raises pupil_labs.realtime_api.device.DeviceError: if the request fails
        """

        async def _get_status():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.get_status()

        return asyncio.run(_get_status())

    @staticmethod
    def _auto_update(
        device_weakref: weakref.ReferenceType["Device"],
        auto_update_started_flag: threading.Event,
    ):
        async def _auto_update_until_closed():
            async with _DeviceAsync.convert_from(device_weakref()) as device:
                should_close_flag = asyncio.Event()
                device_weakref()._should_close_flag = should_close_flag
                await device.start_auto_update(
                    update_callback=device_weakref()._status.update
                )
                auto_update_started_flag.set()
                await should_close_flag.wait()
                await device.stop_auto_update()

        return asyncio.run(_auto_update_until_closed())
