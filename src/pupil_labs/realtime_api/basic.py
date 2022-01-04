import asyncio
import threading
import typing as T

from .base import DeviceBase
from .device import Device as _DeviceAsync
from .discovery import discover_devices as _discover_devices_async
from .models import Event, Status, DiscoveredDeviceInfo


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

    async def _return_first_device() -> DiscoveredDeviceInfo:
        async for dev_info in _discover_devices_async(max_search_duration_seconds):
            return dev_info

    dev_info = asyncio.run(_return_first_device())
    if dev_info is not None:
        return Device.from_discovered_device(dev_info)


class Device(DeviceBase):
    """
    .. hint::
        Use :py:func:`.discover_one_device` or :py:func:`.discovered_devices` instead of
        initializing the class manually. See the :ref:`basic_discovery_example` example.

    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._status = self._get_status()
        self._auto_update_thread = threading.Thread(
            target=self._auto_update,
            name=f"{self} auto-update thread",
        )
        self._auto_update_thread.start()

    def close(self) -> None:
        self._should_close_flag.set()
        self._auto_update_thread.join()
    
    def __del__(self):
        self.close()

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

    def _auto_update(self):
        async def _auto_update_until_closed():
            async with _DeviceAsync.convert_from(self) as device:
                self._should_close_flag = asyncio.Event()
                await device.start_auto_update(self._status.update)
                await self._should_close_flag.wait()
                await device.stop_auto_update()

        return asyncio.run(_auto_update_until_closed())
