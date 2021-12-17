import datetime
import struct
import typing as T

from .base import RTSPData, RTSPRawStreamer, receive_raw_rtsp_data


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


async def receive_gaze_data(url) -> T.AsyncIterator[GazeData]:
    async with RTSPGazeStreamer() as streamer:
        for datum in streamer.receive(url):
            yield datum


class RTSPGazeStreamer(RTSPRawStreamer):
    async def receive(self) -> T.AsyncIterator[GazeData]:
        async for data in super().receive():
            yield GazeData.from_raw(data)
