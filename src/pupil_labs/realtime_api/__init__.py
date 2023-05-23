"""pupil_labs.realtime_api"""


def remove_interleave_assertion_monkeypatch_aiortsp_tcp_transport():
    """
    Remove assertion in aiortsp.transport.tcp.TCPTransport.on_transport_response

    Original code:
    https://github.com/marss/aiortsp/blob/c15c231/aiortsp/transport/tcp.py#L69
    """
    import warnings

    import aiortsp.rtsp.errors
    import aiortsp.transport

    warnings.warn(
        "MONKEYPATCHING aiortsp.transport.tcp.TCPTransport.on_transport_response"
        " to remove interleave assertion"
    )

    def patched_on_tranport_response(self, headers: dict):
        if "transport" not in headers:
            raise aiortsp.rtsp.errors.RTSPError("error on SETUP: Transport not found")

        fields = self.parse_transport_fields(headers["transport"])

        # NOTE: this assertion was removed
        # assert (
        #     fields.get("interleaved") == f"{self.rtp_idx}-{self.rtcp_idx}"
        # ), "invalid returned interleaved header"

    aiortsp.transport.tcp.TCPTransport.on_transport_response = (
        patched_on_tranport_response
    )


remove_interleave_assertion_monkeypatch_aiortsp_tcp_transport()

# .version is generated on install via setuptools_scm, see pyproject.toml
from .device import APIPath, Device, DeviceError, StatusUpdateNotifier
from .discovery import Network, discover_devices
from .streaming import (
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
