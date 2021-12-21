import asyncio
import typing as T

from .base import ControlBase
from .control import Control as _ControlAsync
from .discovery import discover_devices as _discover_devices_async
from .models import Event, Status


def discovered_devices(search_duration_seconds: float) -> T.List["Control"]:
    """Return all devices that could be found in the given search duration."""

    async def _collect_devices():
        return [
            Control.from_discovered_device(dev)
            async for dev in _discover_devices_async(search_duration_seconds)
        ]

    return asyncio.run(_collect_devices())


def discover_one_device(
    max_search_duration_seconds: T.Optional[float],
) -> T.Optional["Control"]:
    """Search until one device is found."""

    async def _return_first_device():
        async for dev in _discover_devices_async(max_search_duration_seconds):
            return Control.from_discovered_device(dev)

    return asyncio.run(_return_first_device())


class Control(ControlBase):
    """
    .. hint::
        Use :py:func:`.discover_one_device` or :py:func:`.discovered_devices` instead of
        initializing the class manually. See the :ref:`basic_discovery_example` example.

    """

    def get_status(self) -> Status:
        """Wraps :py:meth:`pupil_labs.realtime_api.control.Control.get_status`

        :raises pupil_labs.realtime_api.control.ControlError: if the request fails
        """

        async def _get_status():
            async with _ControlAsync.convert_from(self) as control:
                return await control.get_status()

        return asyncio.run(_get_status())

    def recording_start(self) -> str:
        """Wraps :py:meth:`pupil_labs.realtime_api.control.Control.recording_start`

        :raises pupil_labs.realtime_api.control.ControlError:
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
            async with _ControlAsync.convert_from(self) as control:
                return await control.recording_start()

        return asyncio.run(_start_recording())

    def recording_stop_and_save(self):
        """Wraps :py:meth:`pupil_labs.realtime_api.control.Control.recording_stop_and_save`

        :raises pupil_labs.realtime_api.control.ControlError:
            if the recording could not be started
            Possible reasons include
            - Recording not running
            - template has required fields
        """

        async def _stop_and_save_recording():
            async with _ControlAsync.convert_from(self) as control:
                return await control.recording_stop_and_save()

        return asyncio.run(_stop_and_save_recording())

    def recording_cancel(self):
        """Wraps :py:meth:`pupil_labs.realtime_api.control.Control.recording_cancel`

        :raises pupil_labs.realtime_api.control.ControlError:
            if the recording could not be started
            Possible reasons include
            - Recording not running
        """

        async def _cancel_recording():
            async with _ControlAsync.convert_from(self) as control:
                return await control.recording_cancel()

        return asyncio.run(_cancel_recording())

    def send_event(
        self, event_name: str, event_timestamp_unix_ns: T.Optional[int] = None
    ) -> Event:
        """
        :raises pupil_labs.realtime_api.control.ControlError: if sending the event fails
        """

        async def _send_event():
            async with _ControlAsync.convert_from(self) as control:
                return await control.send_event(event_name, event_timestamp_unix_ns)

        return asyncio.run(_send_event())
