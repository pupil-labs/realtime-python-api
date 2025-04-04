import datetime
import logging
import struct
from collections.abc import AsyncIterator
from typing import Any, NamedTuple

from .base import RTSPData, RTSPRawStreamer

logger = logging.getLogger(__name__)


class BlinkEventData(NamedTuple):
    event_type: int
    start_time_ns: int
    end_time_ns: int
    rtp_ts_unix_seconds: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "BlinkEventData":
        (
            event_type,
            start_time_ns,
            end_time_ns,
        ) = struct.unpack("!iqq", data.raw)
        return cls(event_type, start_time_ns, end_time_ns, data.timestamp_unix_seconds)

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.rtp_ts_unix_seconds)

    @property
    def timestamp_unix_ns(self) -> int:
        return int(self.rtp_ts_unix_seconds * 1e9)


class FixationEventData(NamedTuple):
    event_type: int  # 0: Saccade, 1: Fixation
    start_time_ns: int
    end_time_ns: int
    start_gaze_x: float
    start_gaze_y: float
    end_gaze_x: float
    end_gaze_y: float
    mean_gaze_x: float
    mean_gaze_y: float
    amplitude_pixels: float
    amplitude_angle_deg: float
    mean_velocity: float
    max_velocity: float
    rtp_ts_unix_seconds: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "FixationEventData":
        (
            event_type,
            start_time_ns,
            end_time_ns,
            start_gaze_x,
            start_gaze_y,
            end_gaze_x,
            end_gaze_y,
            mean_gaze_x,
            mean_gaze_y,
            amplitude_pixels,
            amplitude_angle_deg,
            mean_velocity,
            max_velocity,
        ) = struct.unpack("!iqqffffffffff", data.raw)
        return cls(
            event_type,
            start_time_ns,
            end_time_ns,
            start_gaze_x,
            start_gaze_y,
            end_gaze_x,
            end_gaze_y,
            mean_gaze_x,
            mean_gaze_y,
            amplitude_pixels,
            amplitude_angle_deg,
            mean_velocity,
            max_velocity,
            data.timestamp_unix_seconds,
        )

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.rtp_ts_unix_seconds)

    @property
    def timestamp_unix_ns(self) -> int:
        return int(self.rtp_ts_unix_seconds * 1e9)


class FixationOnsetEventData(NamedTuple):
    event_type: int  # 0: Saccade, 1: Fixation
    start_time_ns: int
    rtp_ts_unix_seconds: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "FixationOnsetEventData":
        (
            event_type,
            start_time_ns,
        ) = struct.unpack("!iq", data.raw)
        return cls(event_type, start_time_ns, data.timestamp_unix_seconds)

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.rtp_ts_unix_seconds)

    @property
    def timestamp_unix_ns(self) -> int:
        return int(self.rtp_ts_unix_seconds * 1e9)


async def receive_eye_events_data(
    url: str, *args: Any, **kwargs: Any
) -> AsyncIterator[FixationEventData | FixationOnsetEventData | BlinkEventData]:
    async with RTSPEyeEventStreamer(url, *args, **kwargs) as streamer:
        async for datum in streamer.receive():
            yield datum


class RTSPEyeEventStreamer(RTSPRawStreamer):
    async def receive(
        self,
    ) -> AsyncIterator[FixationEventData | FixationOnsetEventData | BlinkEventData]:
        data_class_by_type = {
            0: FixationEventData,
            1: FixationEventData,
            2: FixationOnsetEventData,
            3: FixationOnsetEventData,
            4: BlinkEventData,
            5: None,  # KEEPALIVE MSG, SKIP
        }
        async for data in super().receive():
            try:
                event_type = struct.unpack_from("!i", data.raw)[0]
                cls = data_class_by_type[event_type]
                if cls is not None:
                    yield cls.from_raw(data)
            except KeyError:
                logger.exception(f"Raw eye event data has unexpected type: {data}")
                raise
            except Exception:
                logger.exception(f"Unable to parse eye event data {data}")
                raise
