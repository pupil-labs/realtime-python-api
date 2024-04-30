import datetime
import typing as T

from ..streaming.gaze import DualMonocularGazeData, EyestateGazeData, GazeData
from ..streaming.video import BGRBuffer, VideoFrame

GazeDataType = T.Union[GazeData, DualMonocularGazeData, EyestateGazeData]


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


# The following name can be considered technical debt from the time when there were only
# two streams (scene video and gaze) to match. When I added support for streaming eyes
# video, I thought about giving it a more descriptive name. But since this is an output
# class of the public API, I decided against it to avoid breaking possible imports.
class MatchedItem(T.NamedTuple):
    frame: SimpleVideoFrame
    gaze: GazeDataType


class MatchedGazeEyesSceneItem(T.NamedTuple):
    scene: SimpleVideoFrame
    eyes: SimpleVideoFrame
    gaze: GazeDataType


MATCHED_ITEM_LABEL = "matched_gaze_and_scene_video"
MATCHED_GAZE_EYES_LABEL = "matched_gaze_eyes_and_scene_video"
