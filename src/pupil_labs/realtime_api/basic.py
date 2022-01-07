import asyncio
import collections
import logging
import threading
import typing as T
import weakref

try:
    from typing import Literal
except ImportError:
    # FIXME: Remove when dropping py3.7 support
    from typing_extensions import Literal

from pupil_labs.realtime_api.streaming.gaze import GazeData
from pupil_labs.realtime_api.streaming.video import VideoFrame

from .base import DeviceBase
from .device import Device as _DeviceAsync
from .discovery import discover_devices as _discover_devices_async
from .models import Component, DiscoveredDeviceInfo, Event, Sensor, Status
from .streaming import RTSPGazeStreamer, RTSPVideoFrameStreamer

logger = logging.getLogger(__name__)


class MatchedItem(T.NamedTuple):
    frame: VideoFrame
    gaze: GazeData


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
        self._start_background_worker()

    def close(self) -> None:
        if self._event_should_close:
            self._event_should_close.set()
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
    def battery_state(self) -> Literal["OK", "LOW", "CRITICAL"]:
        return self._status.phone.battery_state

    @property
    def memory_num_free_bytes(self) -> int:
        return self._status.phone.memory

    @property
    def memory_state(self) -> Literal["OK", "LOW", "CRITICAL"]:
        return self._status.phone.memory_state

    @property
    def version_glasses(self) -> str:
        return self._status.hardware.version

    @property
    def serial_number_glasses(self) -> T.Union[str, None, Literal["default"]]:
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

    def read_scene_video_frame(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[VideoFrame]:
        return self._read_item(Sensor.Name.WORLD.value, timeout_seconds)

    def read_gaze_datum(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[GazeData]:
        return self._read_item(Sensor.Name.GAZE.value, timeout_seconds)

    def read_matched_scene_video_frame_and_gaze(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[MatchedItem]:
        return self._read_item(self._MATCHED_ITEM, timeout_seconds)

    def _read_item(
        self, sensor: str, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[T.Union[VideoFrame, GazeData]]:
        try:
            return self._most_recent_item[sensor].popleft()
        except IndexError:
            # no cached frame available, waiting for new one
            event_new_item = self._event_new_item[sensor]
            event_new_item.clear()
            if event_new_item.wait(timeout=timeout_seconds):
                return self._most_recent_item[sensor].popleft()
            return None

    _MATCHED_ITEM = "matched_gaze_and_scene_video"

    def _start_background_worker(self):
        self._event_should_close: T.Optional[asyncio.Event] = None

        # List of sensors that will
        sensor_names = [
            Sensor.Name.GAZE.value,
            Sensor.Name.WORLD.value,
            self._MATCHED_ITEM,
        ]
        self._most_recent_item = {
            name: collections.deque(maxlen=1) for name in sensor_names
        }
        self._event_new_item = {name: threading.Event() for name in sensor_names}
        # only cache 3-4 seconds worth of gaze data in case no scene camera is connected
        GazeCacheType = T.Deque[T.Tuple[float, GazeData]]
        self._cached_gaze_for_matching: GazeCacheType = collections.deque(maxlen=200)

        event_auto_update_started = threading.Event()
        self._auto_update_thread = threading.Thread(
            target=self._auto_update,
            kwargs=dict(
                device_weakref=weakref.ref(self),  # weak ref to avoid cycling ref
                auto_update_started_flag=event_auto_update_started,
            ),
            name=f"{self} auto-update thread",
        )
        self._auto_update_thread.start()
        event_auto_update_started.wait()

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
        device_weakref: weakref.ReferenceType,
        auto_update_started_flag: threading.Event,
    ):
        stream_managers = {
            Sensor.Name.GAZE.value: _StreamManager(device_weakref, RTSPGazeStreamer),
            Sensor.Name.WORLD.value: _StreamManager(
                device_weakref, RTSPVideoFrameStreamer
            ),
        }

        async def _process_status_changes(changed: Component):
            if (
                isinstance(changed, Sensor)
                and changed.conn_type == Sensor.Connection.DIRECT.value
            ):
                if changed.sensor in stream_managers:
                    await stream_managers[changed.sensor].handle_sensor_update(changed)
                else:
                    logger.debug(f"Unhandled DIRECT sensor {changed.name}")

        async def _auto_update_until_closed():
            async with _DeviceAsync.convert_from(device_weakref()) as device:
                should_close_flag = asyncio.Event()
                device_weakref()._event_should_close = should_close_flag
                await device.auto_update_start(
                    update_callback=device_weakref()._status.update,
                    update_callback_async=_process_status_changes,
                )
                auto_update_started_flag.set()
                await should_close_flag.wait()
                await device.auto_update_stop()

        return asyncio.run(_auto_update_until_closed())


class _StreamManager:
    def __init__(
        self,
        device_weakref: weakref.ReferenceType,
        streaming_cls: T.Union[
            T.Type[RTSPVideoFrameStreamer], T.Type[RTSPGazeStreamer]
        ],
    ) -> None:
        self._device = device_weakref
        self._streaming_cls = streaming_cls
        self._streaming_task = None

    async def handle_sensor_update(self, sensor: Sensor):
        if self._streaming_task is not None:
            logger.debug(
                f"Cancelling prior streaming connection to "
                f"{self._streaming_task.get_name()}"
            )
            self._streaming_task.cancel()
            self._streaming_task = None

        if sensor.connected:
            logger.debug(f"Starting stream to {sensor}")
            self._streaming_task = asyncio.create_task(
                self.append_data_from_sensor_to_queue(sensor), name=str(sensor)
            )

    async def append_data_from_sensor_to_queue(self, sensor: Sensor):
        self._device()._cached_gaze_for_matching.clear()
        async with self._streaming_cls(
            sensor.url, run_loop=True, log_level=logging.WARNING
        ) as streamer:
            async for item in streamer.receive():
                device = self._device()
                if device is None:
                    logger.debug("Device reference does no longer exist")
                    break
                name = sensor.sensor
                logger.debug(f"{self} received {item}")
                device._most_recent_item[name].append(item)
                if name == Sensor.Name.GAZE.value:
                    device._cached_gaze_for_matching.append(
                        (item.timestamp_unix_seconds, item)
                    )
                elif name == Sensor.Name.WORLD.value:
                    try:
                        logger.debug(
                            f"Searching closest gaze datum in cache "
                            f"(len={len(device._cached_gaze_for_matching)})..."
                        )
                        gaze = self._get_closest_item(
                            device._cached_gaze_for_matching,
                            item.timestamp_unix_seconds,
                        )
                    except IndexError:
                        logger.debug("No cached gaze data available for matching")
                    else:
                        match_time_difference = (
                            item.timestamp_unix_seconds - gaze.timestamp_unix_seconds
                        )
                        logger.debug(
                            f"Found matching sample (time difference: "
                            f"{match_time_difference:.3f} seconds)"
                        )
                        device._most_recent_item[Device._MATCHED_ITEM].append(
                            MatchedItem(item, gaze)
                        )
                        device._event_new_item[Device._MATCHED_ITEM].set()
                else:
                    logger.error(f"Unhandled {item} for sensor {name}")

                device._event_new_item[name].set()
                del device  # remove Device reference

    @staticmethod
    def _get_closest_item(cache: T.Deque[GazeData], timestamp) -> GazeData:
        item_ts, item = cache.popleft()
        # assumes monotonically increasing timestamps
        if item_ts > timestamp:
            return item
        while True:
            try:
                next_item_ts, next_item = cache.popleft()
            except IndexError:
                return item
            else:
                if next_item_ts > timestamp:
                    return next_item
                item_ts, item = next_item_ts, next_item
