import datetime
import logging
import struct
from collections.abc import AsyncIterator
from typing import Any, NamedTuple

from .base import RTSPData, RTSPRawStreamer
from .basic_models import Point

logger = logging.getLogger(__name__)


class BlinkEventData(NamedTuple):
    """Data for a blink event.

    Represents a detected blink event with timing information.

    Attributes:
        event_type (int): Type of event (4 for blink events).
        start_time_ns (int): Start time of the blink in nanoseconds.
        end_time_ns (int): End time of the blink in nanoseconds.
        rtp_ts_unix_seconds (float): RTP timestamp in seconds since Unix epoch.

    """

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
    """Data for a fixation or saccade event.

    Represents a completed fixation or saccade event with detailed information.

    Attributes:
        event_type (int): Type of event (0 for saccade, 1 for fixation).
        start_time_ns (int): Start time in nanoseconds.
        end_time_ns (int): End time in nanoseconds.
        start_gaze (Point): Fixation point coordinates at start of event.
        end_gaze (Point): Fixation point coordinates at end of event.
        mean_gaze (Point): Mean fixation coordinates during event.
        amplitude_pixels (float): Amplitude of the event in pixels.
        amplitude_angle_deg (float): Amplitude of the event in degrees.
        mean_velocity (float): Mean velocity during the event.
        max_velocity (float): Maximum velocity during the event.
        rtp_ts_unix_seconds (float): RTP timestamp in seconds since Unix epoch.

    """

    event_type: int
    start_time_ns: int
    end_time_ns: int
    start_gaze: Point
    end_gaze: Point
    mean_gaze: Point
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
            start_gaze=Point(x=start_gaze_x, y=start_gaze_y),
            end_gaze=Point(x=end_gaze_x, y=end_gaze_y),
            mean_gaze=Point(x=mean_gaze_x, y=mean_gaze_y),
            amplitude_pixels=amplitude_pixels,
            amplitude_angle_deg=amplitude_angle_deg,
            mean_velocity=mean_velocity,
            max_velocity=max_velocity,
            rtp_ts_unix_seconds=data.timestamp_unix_seconds,
        )

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.rtp_ts_unix_seconds)

    @property
    def timestamp_unix_ns(self) -> int:
        return int(self.rtp_ts_unix_seconds * 1e9)


class FixationOnsetEventData(NamedTuple):
    """Data for a fixation or saccade onset event.

    Represents the beginning of a fixation or saccade event.

    Attributes:
        event_type (int): Type of event (2 for saccade onset, 3 for fixation onset).
        start_time_ns (int): Start time in nanoseconds.
        rtp_ts_unix_seconds (float): RTP timestamp in seconds since Unix epoch.

    """

    event_type: int
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
    """Receive eye events data from an RTSP stream.

    This is a convenience function that creates an RTSPEyeEventStreamer and yields
    parsed eye event data.

    Args:
        url: RTSP URL to connect to.
        *args: Additional positional arguments passed to RTSPEyeEventStreamer.
        **kwargs: Additional keyword arguments passed to RTSPEyeEventStreamer.

    Yields:
        FixationEventData: Parsed fixation event data.

    """
    async with RTSPEyeEventStreamer(url, *args, **kwargs) as streamer:
        async for datum in streamer.receive():
            yield datum  # type: ignore


class RTSPEyeEventStreamer(RTSPRawStreamer):
    """Stream and parse eye events from an RTSP source.

    This class extends RTSPRawStreamer to parse raw RTSP data into structured
    eye event data objects.
    """

    async def receive(  # type: ignore[override]
        self,
    ) -> AsyncIterator[FixationEventData | FixationOnsetEventData | BlinkEventData]:
        """Receive and parse eye events from the RTSP stream.

        Yields:
            FixationEventData | FixationOnsetEventData | BlinkEventData: Parsed eye
                event data.

        Raises:
            KeyError: If the event type is not recognized.
            Exception: If there is an error parsing the event data.

        """
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
                    yield cls.from_raw(data)  # type: ignore[attr-defined]
            except KeyError:
                logger.exception(f"Raw eye event data has unexpected type: {data}")
                raise
            except Exception:
                logger.exception(f"Unable to parse eye event data {data}")
                raise
