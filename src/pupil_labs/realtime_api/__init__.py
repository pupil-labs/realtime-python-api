"""pupil_labs.realtime_api"""

# .version is generated on install via setuptools_scm, see pyproject.toml
from .device import APIPath, Device, DeviceError, StatusUpdateNotifier
from .discovery import Network, discover_devices
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
    "__version__",
    "__version_info__",
    "APIPath",
    "Device",
    "DeviceError",
    "discover_devices",
    "GazeData",
    "Network",
    "receive_gaze_data",
    "receive_raw_rtsp_data",
    "receive_video_frames",
    "RTSPData",
    "RTSPGazeStreamer",
    "RTSPRawStreamer",
    "RTSPVideoFrameStreamer",
    "StatusUpdateNotifier",
    "VideoFrame",
]
