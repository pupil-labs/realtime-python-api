import base64
import datetime
import logging
import typing as T

import av
import nptyping as npt

from .base import RTSPRawStreamer, SDPDataNotAvailableError
from .nal_unit import extract_payload_from_nal_unit

logger = logging.getLogger(__name__)

BGRBuffer = npt.NDArray[(1080, 1088, 3), npt.UInt8]
"""Type annotation for raw BGR image buffers of the scene camera"""


class VideoFrame(T.NamedTuple):
    av_frame: av.VideoFrame
    timestamp_unix_seconds: float

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self):
        return int(self.timestamp_unix_seconds * 1e9)

    def to_ndarray(self, *args, **kwargs):
        return self.av_frame.to_ndarray(*args, **kwargs)

    def bgr_buffer(self) -> BGRBuffer:
        return self.to_ndarray(format="bgr24")


async def receive_video_frames(url, *args, **kwargs) -> T.AsyncIterator[VideoFrame]:
    async with RTSPVideoFrameStreamer(url, *args, **kwargs) as streamer:
        async for datum in streamer.receive():
            yield datum


class RTSPVideoFrameStreamer(RTSPRawStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sprop_parameter_set_payloads = None

    async def receive(self) -> T.AsyncIterator[VideoFrame]:
        codec = None
        frame_timestamp = None

        async for data in super().receive():
            if not codec:
                try:
                    codec = av.CodecContext.create(self.encoding, "r")
                    for param in self.sprop_parameter_set_payloads:
                        codec.parse(param)
                except SDPDataNotAvailableError as err:
                    logger.debug(
                        f"Session description protocol data not available yet: {err}"
                    )
                    continue
            # if pkt is the start of a new fragmented frame, parse will return a packet
            # containing the data from the previous fragments
            for packet in codec.parse(extract_payload_from_nal_unit(data.raw)):
                # use timestamp of previous packets
                for av_frame in codec.decode(packet):
                    yield VideoFrame(av_frame, frame_timestamp)

            frame_timestamp = data.timestamp_unix_seconds

    @property
    def sprop_parameter_set_payloads(self) -> T.Optional[T.List[T.ByteString]]:
        """:raises pupil_labs.realtime_api.streaming.base.SDPDataNotAvailableError:"""
        if self._sprop_parameter_set_payloads is None:
            try:
                attributes = self.reader.session.sdp["medias"][0]["attributes"]
                sprop_parameter_sets = attributes["fmtp"]["sprop-parameter-sets"]
                params = (
                    base64.b64decode(param) for param in sprop_parameter_sets.split(",")
                )
                self._sprop_parameter_set_payloads = [
                    extract_payload_from_nal_unit(param) for param in params
                ]
            except (IndexError, KeyError) as err:
                raise SDPDataNotAvailableError(
                    f"SDP data is missing {err} field"
                ) from err

        return self._sprop_parameter_set_payloads
