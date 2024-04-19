import datetime
import logging
import struct
import typing as T

from .base import RTSPData, RTSPRawStreamer

logger = logging.getLogger(__name__)


class Point(T.NamedTuple):
    x: float
    y: float


class GazeData(T.NamedTuple):
    x: float
    y: float
    worn: bool
    timestamp_unix_seconds: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "GazeData":
        x, y, worn = struct.unpack("!ffB", data.raw)
        return cls(x, y, worn == 255, data.timestamp_unix_seconds)

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self):
        return int(self.timestamp_unix_seconds * 1e9)


class DualMonocularGazeData(T.NamedTuple):
    """EXPERIMENTAL CLASS"""

    left: Point
    right: Point
    worn: bool
    timestamp_unix_seconds: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "GazeData":
        x1, y1, worn, x2, y2 = struct.unpack("!ffBff", data.raw)
        return cls(
            Point(x1, y1), Point(x2, y2), worn == 255, data.timestamp_unix_seconds
        )

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self):
        return int(self.timestamp_unix_seconds * 1e9)


class EyestateGazeData(T.NamedTuple):
    x: float
    y: float
    worn: bool
    pupil_diameter_left: float
    eyeball_center_left_x: float
    eyeball_center_left_y: float
    eyeball_center_left_z: float
    optical_axis_left_x: float
    optical_axis_left_y: float
    optical_axis_left_z: float
    pupil_diameter_right: float
    eyeball_center_right_x: float
    eyeball_center_right_y: float
    eyeball_center_right_z: float
    optical_axis_right_x: float
    optical_axis_right_y: float
    optical_axis_right_z: float
    timestamp_unix_seconds: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "EyestateGazeData":
        (
            x,
            y,
            worn,
            pupil_diameter_left,
            eyeball_center_left_x,
            eyeball_center_left_y,
            eyeball_center_left_z,
            optical_axis_left_x,
            optical_axis_left_y,
            optical_axis_left_z,
            pupil_diam_right,
            eyeball_center_right_x,
            eyeball_center_right_y,
            eyeball_center_right_z,
            optical_axis_right_x,
            optical_axis_right_y,
            optical_axis_right_z,
        ) = struct.unpack("!ffBffffffffffffff", data.raw)
        return cls(
            x,
            y,
            worn == 255,
            pupil_diameter_left,
            eyeball_center_left_x,
            eyeball_center_left_y,
            eyeball_center_left_z,
            optical_axis_left_x,
            optical_axis_left_y,
            optical_axis_left_z,
            pupil_diam_right,
            eyeball_center_right_x,
            eyeball_center_right_y,
            eyeball_center_right_z,
            optical_axis_right_x,
            optical_axis_right_y,
            optical_axis_right_z,
            data.timestamp_unix_seconds,
        )

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self):
        return int(self.timestamp_unix_seconds * 1e9)


async def receive_gaze_data(
    url, *args, **kwargs
) -> T.AsyncIterator[T.Union[GazeData, DualMonocularGazeData, EyestateGazeData]]:
    async with RTSPGazeStreamer(url, *args, **kwargs) as streamer:
        async for datum in streamer.receive():
            yield datum


class RTSPGazeStreamer(RTSPRawStreamer):
    async def receive(
        self,
    ) -> T.AsyncIterator[T.Union[GazeData, DualMonocularGazeData, EyestateGazeData]]:
        data_class_by_raw_len = {
            9: GazeData,
            17: DualMonocularGazeData,
            65: EyestateGazeData,
        }
        async for data in super().receive():
            try:
                cls = data_class_by_raw_len[len(data.raw)]
                yield cls.from_raw(data)
            except KeyError:
                logger.exception(f"Raw gaze data has unexpected length: {data}")
                raise
            except Exception:
                logger.exception(f"Unable to parse gaze data {data}")
                raise
