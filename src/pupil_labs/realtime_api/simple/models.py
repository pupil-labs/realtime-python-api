import datetime
import typing as T

from ..streaming.gaze import GazeData
from ..streaming.video import BGRBuffer, VideoFrame


class SimpleVideoFrame(T.NamedTuple):
    bgr_pixels: BGRBuffer
    timestamp_unix_seconds: float

    @classmethod
    def from_video_frame(cls, vf: VideoFrame) -> "SimpleVideoFrame":
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


MATCHED_ITEM_LABEL = "matched_gaze_and_scene_video"
