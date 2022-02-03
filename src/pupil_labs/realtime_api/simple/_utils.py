from __future__ import annotations

import asyncio
import logging
import typing as T
import weakref
from collections.abc import Hashable, Iterable, Mapping
from types import MappingProxyType

from ..models import Sensor
from ..streaming import RTSPGazeStreamer, RTSPVideoFrameStreamer
from .models import MATCHED_ITEM_LABEL, GazeData, MatchedItem, SimpleVideoFrame

logger_name = "pupil_labs.realtime_api.simple"
logger = logging.getLogger(logger_name)
logger_receive_data = logging.getLogger(logger_name + ".Device.receive_data")
logger_receive_data.setLevel(logging.INFO)


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
                        device._most_recent_item[MATCHED_ITEM_LABEL].append(
                            MatchedItem(item, gaze)
                        )
                        device._event_new_item[MATCHED_ITEM_LABEL].set()
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


__all__ = ["_AsyncEventManager", "_StreamManager"]
