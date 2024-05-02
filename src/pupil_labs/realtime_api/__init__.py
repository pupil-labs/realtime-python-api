"""pupil_labs.realtime_api"""

# .version is generated on install via setuptools_scm, see pyproject.toml
from .device import APIPath, Device, DeviceError, StatusUpdateNotifier
from .discovery import Network, discover_devices
from .streaming import (
    DualMonocularGazeData,
    EyestateGazeData,
    GazeData,
    RTSPData,
    RTSPGazeStreamer,
    RTSPImuStreamer,
    RTSPRawStreamer,
    RTSPVideoFrameStreamer,
    VideoFrame,
    receive_gaze_data,
    receive_imu_data,
    receive_raw_rtsp_data,
    receive_video_frames,
)

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("pupil_labs.realtime_api")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "__version__",
    "APIPath",
    "Device",
    "DeviceError",
    "discover_devices",
    "GazeData",
    "DualMonocularGazeData",
    "EyestateGazeData",
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
    "receive_imu_data",
    "RTSPImuStreamer",
    "imu_pb2",
]
