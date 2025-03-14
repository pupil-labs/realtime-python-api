import asyncio
import collections
import enum
import threading
import typing as T
import weakref
from uuid import UUID

from typing_extensions import Literal

from ..base import DeviceBase
from ..device import Device as _DeviceAsync
from ..device import StatusUpdateNotifier
from ..models import Component, Event, Sensor, Status, Template, TemplateDataFormat
from ..streaming import (
    ImuPacket,
    RTSPGazeStreamer,
    RTSPImuStreamer,
    RTSPVideoFrameStreamer,
)
from ..time_echo import TimeEchoEstimates, TimeOffsetEstimator
from ._utils import _AsyncEventManager, _StreamManager, logger
from .models import (
    MATCHED_GAZE_EYES_LABEL,
    MATCHED_ITEM_LABEL,
    GazeDataType,
    MatchedGazeEyesSceneItem,
    MatchedItem,
    SimpleVideoFrame,
    VideoFrame,
)


class Device(DeviceBase):
    """
    .. hint::
        Use :py:func:`pupil_labs.realtime_api.simple.discover_devices` instead of
        initializing the class manually. See the :ref:`simple_discovery_example`
        example.
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
    def module_serial(self) -> T.Union[str, None, Literal["default"]]:
        """Returns ``None`` or ``"default"`` if no glasses are connected"""
        return self._status.hardware.module_serial

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

    def get_calibration(self):
        async def _get_calibration():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.get_calibration()

        return asyncio.run(_get_calibration())

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
        """Wraps
        :py:meth:`pupil_labs.realtime_api.device.Device.recording_stop_and_save`

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

    def get_template(self) -> Template:
        """
        Wraps :py:meth:`pupil_labs.realtime_api.device.Device.get_template`

        Gets the template currently selected on device

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the template can't be fetched.
        """

        async def _get_template():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.get_template()

        return asyncio.run(_get_template())

    def get_template_data(self, format: TemplateDataFormat = "simple"):
        """
        Wraps :py:meth:`pupil_labs.realtime_api.device.Device.get_template_data`

        Gets the template data entered on device

        :param str format: "simple" | "api"
            "api" returns the data as is from the api eg. {"item_uuid": ["42"]}
            "simple" returns the data parsed eg. {"item_uuid": 42}

        :raises pupil_labs.realtime_api.device.DeviceError:
                if the template's data could not be fetched
        """

        async def _get_template_data():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.get_template_data(format=format)

        return asyncio.run(_get_template_data())

    def post_template_data(self, template_data, format: TemplateDataFormat = "simple"):
        """
        Wraps :py:meth:`pupil_labs.realtime_api.device.Device.post_template_data`

        Sets the data for the currently selected template

        :param str format: "simple" | "api"
            "api" accepts the data as in realtime api format eg. {"item_uuid": ["42"]}
            "simple" accepts the data in parsed format eg. {"item_uuid": 42}

        :raises pupil_labs.realtime_api.device.DeviceError:
            if the data can not be sent.
            ValueError: if invalid data type.
        """

        async def _post_template_data():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.post_template_data(template_data, format=format)

        return asyncio.run(_post_template_data())

    def get_question_by_id(self, question_id: T.Union[str, UUID]):
        async def _get_question_by_id():
            async with _DeviceAsync.convert_from(self) as control:
                return await control.get_question_by_id(question_id)

        return asyncio.run(_get_question_by_id())

    def receive_scene_video_frame(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[SimpleVideoFrame]:
        return self._receive_item(Sensor.Name.WORLD.value, timeout_seconds)

    def receive_gaze_datum(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[GazeDataType]:
        return self._receive_item(Sensor.Name.GAZE.value, timeout_seconds)

    def receive_eyes_video_frame(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[SimpleVideoFrame]:
        return self._receive_item(Sensor.Name.EYES.value, timeout_seconds)

    def receive_imu_datum(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[ImuPacket]:
        return self._receive_item(Sensor.Name.IMU.value, timeout_seconds)

    def receive_matched_scene_video_frame_and_gaze(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[MatchedItem]:
        return self._receive_item(MATCHED_ITEM_LABEL, timeout_seconds)

    def receive_matched_scene_and_eyes_video_frames_and_gaze(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[MatchedGazeEyesSceneItem]:
        return self._receive_item(MATCHED_GAZE_EYES_LABEL, timeout_seconds)

    def _receive_item(
        self, sensor: str, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[T.Union[VideoFrame, GazeDataType]]:
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

    def estimate_time_offset(
        self,
        number_of_measurements: int = 100,
        sleep_between_measurements_seconds: T.Optional[float] = None,
    ) -> T.Optional[TimeEchoEstimates]:
        """Estimate the time offset between the host device and the client.

        See :py:mod:`pupil_labs.realtime_api.time_echo` for details.
        """
        if self._status.phone.time_echo_port is None:
            logger.warning(
                "You Pupil Invisible Companion app is out-of-date and does not yet "
                "support the Time Echo protocol. Upgrade to version 1.4.28 or newer."
            )
            return None
        estimator = TimeOffsetEstimator(
            self.phone_ip, self._status.phone.time_echo_port
        )
        return asyncio.run(
            estimator.estimate(
                number_of_measurements, sleep_between_measurements_seconds
            )
        )

    def close(self) -> None:
        if self._event_manager:
            if self.is_currently_streaming:
                self.streaming_stop()
            self._event_manager.trigger_threadsafe(self._EVENT.SHOULD_WORKER_CLOSE)
            self._auto_update_thread.join()

    def __del__(self):
        self.close()

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
            Sensor.Name.EYES.value,
            Sensor.Name.IMU.value,
            MATCHED_ITEM_LABEL,
            MATCHED_GAZE_EYES_LABEL,
        ]
        self._most_recent_item = {
            name: collections.deque(maxlen=1) for name in sensor_names
        }
        self._event_new_item = {name: threading.Event() for name in sensor_names}
        # only cache 3-4 seconds worth of gaze data in case no scene camera is connected
        GazeCacheType = T.Deque[T.Tuple[float, GazeDataType]]
        EyesCacheType = T.Deque[T.Tuple[float, SimpleVideoFrame]]
        self._cached_gaze_for_matching: GazeCacheType = collections.deque(maxlen=200)
        self._cached_eyes_for_matching: EyesCacheType = collections.deque(maxlen=200)

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
            Sensor.Name.EYES.value: _StreamManager(
                device_weakref,
                RTSPVideoFrameStreamer,
                should_be_streaming_by_default=start_streaming_by_default,
            ),
            Sensor.Name.IMU.value: _StreamManager(
                device_weakref,
                RTSPImuStreamer,
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
                    logger.debug(f"Unhandled DIRECT sensor {changed.sensor}")

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
                    logger.debug("Background worker waiting for event...")
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
