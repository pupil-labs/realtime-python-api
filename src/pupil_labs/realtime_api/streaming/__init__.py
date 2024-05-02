import typing as T

from .base import (
    RTSPData,
    RTSPRawStreamer,
    SDPDataNotAvailableError,
    receive_raw_rtsp_data,
)
from .gaze import (
    DualMonocularGazeData,
    EyestateGazeData,
    GazeData,
    RTSPGazeStreamer,
    receive_gaze_data,
)
from .imu import RTSPImuStreamer, receive_imu_data
from .imu_pb2 import ImuPacket
from .video import RTSPVideoFrameStreamer, VideoFrame, receive_video_frames

RTSPStreamerType = T.TypeVar("RTSPStreamerType", bound="RTSPRawStreamer")
"""Type annotation for RTSP Streamer classes"""

__all__ = [
    "GazeData",
    "DualMonocularGazeData",
    "EyestateGazeData",
    "receive_gaze_data",
    "receive_raw_rtsp_data",
    "receive_video_frames",
    "RTSPData",
    "RTSPGazeStreamer",
    "RTSPRawStreamer",
    "RTSPVideoFrameStreamer",
    "SDPDataNotAvailableError",
    "VideoFrame",
    "RTSPImuStreamer",
    "receive_imu_data",
    "ImuPacket",
    "imu_pb2",
]
