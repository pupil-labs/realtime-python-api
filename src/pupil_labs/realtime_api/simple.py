from __future__ import annotations

import asyncio
import collections
import datetime
import enum
import logging
import threading
import typing as T
import weakref
from collections.abc import Hashable, Iterable, Mapping
from types import MappingProxyType

try:
    from typing import Literal
except ImportError:
    # FIXME: Remove when dropping py3.7 support
    from typing_extensions import Literal

from pupil_labs.realtime_api.streaming.gaze import GazeData
from pupil_labs.realtime_api.streaming.video import VideoFrame

from .base import DeviceBase
from .device import Device as _DeviceAsync
from .device import StatusUpdateNotifier
from .discovery import discover_devices as _discover_devices_async
from .discovery import discover_one_device as _discover_one_device_async
from .models import Component, DiscoveredDeviceInfo, Event, Sensor, Status
from .streaming import RTSPGazeStreamer, RTSPVideoFrameStreamer
from .streaming.video import BGRBuffer

logger = logging.getLogger(__name__)
logger_receive_data = logging.getLogger(__name__ + ".Device.receive_data")
logger_receive_data.setLevel(logging.INFO)


class SimpleVideoFrame(T.NamedTuple):
    bgr_pixels: BGRBuffer
    timestamp_unix_seconds: float

    @classmethod
    def from_video_frame(cls, vf: VideoFrame) -> SimpleVideoFrame:
        return cls(vf.bgr_buffer(), vf.timestamp_unix_seconds)

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self):
        return int(self.timestamp_unix_seconds * 1e9)


class MatchedItem(T.NamedTuple):
    frame: SimpleVideoFrame
    gaze: GazeData


def discover_devices(search_duration_seconds: float) -> T.List[Device]:
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
) -> T.Optional[Device]:
    """Search until one device is found."""
    dev_info = asyncio.run(_discover_one_device_async(max_search_duration_seconds))
    if dev_info is not None:
        return Device.from_discovered_device(dev_info)
    return None


class Device(DeviceBase):
    """
    .. hint::
        Use :py:func:`.discover_one_device` or :py:func:`.discover_devices` instead of
        initializing the class manually. See the :ref:`simple_discovery_example` example.

    """

    def __init__(
        self,
        address: str,
        port: int,
        full_name: T.Optional[str] = None,
        dns_name: T.Optional[str] = None,
        start_streaming_by_default: bool = False,
        suppress_decoding_warnings: bool = True,
    ) -> None:
        super().__init__(
            address,
            port,
            full_name=full_name,
            dns_name=dns_name,
            suppress_decoding_warnings=suppress_decoding_warnings,
        )
        self._status = self._get_status()
        self._start_background_worker(start_streaming_by_default)

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

    def receive_scene_video_frame(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[SimpleVideoFrame]:
        return self._receive_item(Sensor.Name.WORLD.value, timeout_seconds)

    def receive_gaze_datum(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[GazeData]:
        return self._receive_item(Sensor.Name.GAZE.value, timeout_seconds)

    def receive_matched_scene_video_frame_and_gaze(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[MatchedItem]:
        return self._receive_item(self._MATCHED_ITEM, timeout_seconds)

    def _receive_item(
        self, sensor: str, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[T.Union[VideoFrame, GazeData]]:
        if not self.is_currently_streaming:
            logger.debug("receive_* called without being streaming")
            self.streaming_start()
        try:
            return self._most_recent_item[sensor].popleft()
        except IndexError:
            # no cached frame available, waiting for new one
            event_new_item = self._event_new_item[sensor]
            event_new_item.clear()
            if event_new_item.wait(timeout=timeout_seconds):
                return self._most_recent_item[sensor].popleft()
            return None

    def streaming_start(self):
        self._streaming_trigger_action(self._EVENT.SHOULD_STREAMS_START)

    def streaming_stop(self):
        self._streaming_trigger_action(self._EVENT.SHOULD_STREAMS_STOP)

    def _streaming_trigger_action(self, action):
        if self._event_manager and self._background_loop:
            logger.debug(f"Sending {action.name} trigger")
            self._event_manager.trigger_threadsafe(action)
        else:
            logger.debug(f"Could send {action.name} trigger")

    @property
    def is_currently_streaming(self) -> bool:
        is_streaming = self._is_streaming_flag.is_set()
        return is_streaming

    def close(self) -> None:
        if self._event_manager:
            if self.is_currently_streaming:
                self.streaming_stop()
            self._event_manager.trigger_threadsafe(self._EVENT.SHOULD_WORKER_CLOSE)
            self._auto_update_thread.join()

    def __del__(self):
        self.close()

    _MATCHED_ITEM = "matched_gaze_and_scene_video"

    class _EVENT(enum.Enum):
        SHOULD_WORKER_CLOSE = "should worker close"
        SHOULD_STREAMS_START = "should stream start"
        SHOULD_STREAMS_STOP = "should streams stop"

    def _start_background_worker(self, start_streaming_by_default):
        self._event_manager = None
        self._background_loop = None

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
        self._is_streaming_flag = threading.Event()
        self._auto_update_thread = threading.Thread(
            target=self._auto_update,
            kwargs=dict(
                device_weakref=weakref.ref(self),  # weak ref to avoid cycling ref
                auto_update_started_flag=event_auto_update_started,
                is_streaming_flag=self._is_streaming_flag,
                start_streaming_by_default=start_streaming_by_default,
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
        is_streaming_flag: threading.Event,
        start_streaming_by_default: bool = False,
    ):
        stream_managers = {
            Sensor.Name.GAZE.value: _StreamManager(
                device_weakref,
                RTSPGazeStreamer,
                should_be_streaming_by_default=start_streaming_by_default,
            ),
            Sensor.Name.WORLD.value: _StreamManager(
                device_weakref,
                RTSPVideoFrameStreamer,
                should_be_streaming_by_default=start_streaming_by_default,
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
                event_manager = _AsyncEventManager(Device._EVENT)
                device_weakref()._event_manager = event_manager
                device_weakref()._background_loop = asyncio.get_running_loop()

                notifier = StatusUpdateNotifier(
                    device,
                    callbacks=[
                        device_weakref()._status.update,
                        _process_status_changes,
                    ],
                )
                await notifier.receive_updates_start()
                auto_update_started_flag.set()
                if start_streaming_by_default:
                    logger.debug("Streaming started by default")
                    is_streaming_flag.set()

                while True:
                    logger.debug(f"Background worker waiting for event...")
                    event = await event_manager.wait_for_first_event()
                    logger.debug(f"Background worker received {event}")
                    if event is Device._EVENT.SHOULD_WORKER_CLOSE:
                        break
                    elif event is Device._EVENT.SHOULD_STREAMS_START:
                        for manager in stream_managers.values():
                            manager.should_be_streaming = True
                        is_streaming_flag.set()
                        logger.debug("Streaming started")
                    elif event is Device._EVENT.SHOULD_STREAMS_STOP:
                        for manager in stream_managers.values():
                            manager.should_be_streaming = False
                        is_streaming_flag.clear()
                        logger.debug("Streaming stopped")
                    else:
                        raise RuntimeError(f"Unhandled {event!r}")

                await notifier.receive_updates_stop()
                device_weakref()._event_manager = None

        return asyncio.run(_auto_update_until_closed())


EventKey = T.TypeVar("EventKey", bound=Hashable, covariant=True)


class _AsyncEventManager(T.Generic[EventKey]):
    def __init__(
        self,
        names_to_register: Iterable[EventKey],
    ) -> None:
        self._loop = asyncio.get_running_loop()
        self._events = {name: asyncio.Event() for name in names_to_register}
        if not self._events:
            raise ValueError("Requires at least one event key to register")

    @property
    def events(self) -> Mapping[EventKey, asyncio.Event]:
        return MappingProxyType(self._events)

    def trigger(self, name: EventKey) -> None:
        self._events[name].set()

    def trigger_threadsafe(
        self, name: EventKey, loop: T.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        loop = loop or self._loop
        loop.call_soon_threadsafe(self.trigger, name)

    async def wait_for_first_event(self) -> EventKey:
        tasks = {
            asyncio.create_task(event.wait()): name
            for name, event in self._events.items()
        }
        done, pending = await asyncio.wait(
            tasks.keys(), return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        first_task = next(iter(done))
        event_key = tasks[first_task]
        self._events[event_key].clear()
        return event_key


class _StreamManager:
    def __init__(
        self,
        device_weakref: weakref.ReferenceType,
        streaming_cls: T.Union[
            T.Type[RTSPVideoFrameStreamer], T.Type[RTSPGazeStreamer]
        ],
        should_be_streaming_by_default: bool = False,
    ) -> None:
        self._device = device_weakref
        self._streaming_cls = streaming_cls
        self._streaming_task = None
        self._should_be_streaming = should_be_streaming_by_default
        self._recent_sensor: T.Optional[Sensor] = None

    @property
    def should_be_streaming(self) -> bool:
        return self._should_be_streaming

    @should_be_streaming.setter
    def should_be_streaming(self, should_stream: bool):
        if self._should_be_streaming == should_stream:
            return  # state is already set to desired value
        self._should_be_streaming = should_stream
        if should_stream and self._recent_sensor is not None:
            self._start_streaming_task_if_intended(self._recent_sensor)
        elif not should_stream:
            self._stop_streaming_task_if_running()

    async def handle_sensor_update(self, sensor: Sensor):
        self._stop_streaming_task_if_running()
        self._start_streaming_task_if_intended(sensor)
        self._recent_sensor = sensor

    def _start_streaming_task_if_intended(self, sensor):
        if sensor.connected and self.should_be_streaming:
            logger_receive_data.info(f"Starting stream to {sensor}")
            self._streaming_task = asyncio.create_task(
                self.append_data_from_sensor_to_queue(sensor)
            )

    def _stop_streaming_task_if_running(self):
        if self._streaming_task is not None:
            logger_receive_data.info(
                f"Cancelling prior streaming connection to "
                f"{self._recent_sensor.sensor}"
            )
            self._streaming_task.cancel()
            self._streaming_task = None

    async def append_data_from_sensor_to_queue(self, sensor: Sensor):
        self._device()._cached_gaze_for_matching.clear()
        async with self._streaming_cls(
            sensor.url, run_loop=True, log_level=logging.WARNING
        ) as streamer:
            async for item in streamer.receive():
                device = self._device()
                if device is None:
                    logger_receive_data.info("Device reference does no longer exist")
                    break
                name = sensor.sensor

                if name == Sensor.Name.WORLD.value:
                    # convert to simple video frame
                    item = SimpleVideoFrame.from_video_frame(item)

                logger_receive_data.debug(f"{self} received {item}")
                device._most_recent_item[name].append(item)
                if name == Sensor.Name.GAZE.value:
                    device._cached_gaze_for_matching.append(
                        (item.timestamp_unix_seconds, item)
                    )
                elif name == Sensor.Name.WORLD.value:
                    try:
                        logger_receive_data.debug(
                            f"Searching closest gaze datum in cache "
                            f"(len={len(device._cached_gaze_for_matching)})..."
                        )
                        gaze = self._get_closest_item(
                            device._cached_gaze_for_matching,
                            item.timestamp_unix_seconds,
                        )
                    except IndexError:
                        logger_receive_data.info(
                            "No cached gaze data available for matching"
                        )
                    else:
                        match_time_difference = (
                            item.timestamp_unix_seconds - gaze.timestamp_unix_seconds
                        )
                        logger_receive_data.info(
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
