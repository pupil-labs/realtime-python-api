"""pupil_labs.realtime_api"""

# .version is generated on install via setuptools_scm, see pyproject.toml
from .control import APIPath, Control, ControlError
from .discovery import discover_devices
from .streaming import (
    GazeData,
    RTSPData,
    RTSPGazeStreamer,
    RTSPRawStreamer,
    RTSPVideoFrameStreamer,
    VideoFrame,
    receive_gaze_data,
    receive_raw_rtsp_data,
    receive_video_frames,
)
from .version import __version__, __version_info__

__all__ = [
    "APIPath",
    "Control",
    "ControlError",
    "discover_devices",
    "GazeData",
    "receive_gaze_data",
    "receive_raw_rtsp_data",
    "receive_video_frames",
    "RTSPData",
    "RTSPGazeStreamer",
    "RTSPRawStreamer",
    "RTSPVideoFrameStreamer",
    "VideoFrame",
]
