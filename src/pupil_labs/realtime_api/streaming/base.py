import datetime
import logging
from collections.abc import AsyncIterator, ByteString
from typing import Any, NamedTuple, TypeAlias

from aiortsp.rtcp.parser import SR, RTCPPacket
from aiortsp.rtsp.reader import RTSPReader

AiortspSR: TypeAlias = SR
AiortspRTCPPacket: TypeAlias = RTCPPacket
AiortspRTSPReader: TypeAlias = RTSPReader

logger = logging.getLogger(__name__)


class SDPDataNotAvailableError(Exception):
    pass


class RTSPData(NamedTuple):
    raw: ByteString
    timestamp_unix_seconds: float

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self) -> int:
        return int(self.timestamp_unix_seconds * 1e9)


async def receive_raw_rtsp_data(
    url: str, *args: Any, **kwargs: Any
) -> AsyncIterator[RTSPData]:
    async with RTSPRawStreamer(url, *args, **kwargs) as streamer:
        for datum in streamer.receive():
            yield datum


class RTSPRawStreamer:
    """Forwards all arguments to

    `aiortsp.rtsp.reader.RTSPReader
    <https://github.com/marss/aiortsp/blob/master/aiortsp/rtsp/reader.py#L31-L32>`_
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._reader = _WallclockRTSPReader(*args, **kwargs)
        self._encoding = None

    async def receive(self) -> AsyncIterator[RTSPData]:
        async for pkt in self.reader.iter_packets():
            try:
                timestamp_seconds = self.reader.absolute_timestamp_from_packet(pkt)
            except _UnknownClockoffsetError:
                # The absolute timestamp is not known yet.
                # Waiting for the first RTCP SR packet...
                continue
            yield RTSPData(pkt.data, timestamp_seconds)

    @property
    def reader(self) -> "_WallclockRTSPReader":
        return self._reader

    @property
    def encoding(self) -> str:
        """:raises pupil_labs.realtime_api.streaming.base.SDPDataNotAvailableError:"""
        if self._encoding is None:
            try:
                rtpmap = self._reader.get_rtpmap()
                self._encoding = rtpmap["encoding"].lower()
            except (IndexError, KeyError) as err:
                raise SDPDataNotAvailableError(
                    f"SDP data is missing {err} field"
                ) from err
        return self._encoding

    async def __aenter__(self, *args: Any, **kwargs: Any) -> "RTSPRawStreamer":
        await self.reader.__aenter__(*args, **kwargs)
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.reader.__aexit__(*args, **kwargs)


class _UnknownClockoffsetError(Exception):
    pass


class _WallclockRTSPReader(AiortspRTSPReader):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._relative_to_ntp_clock_offset = None

    def handle_rtcp(self, rtcp: Any) -> None:
        for pkt in rtcp.packets:
            if isinstance(pkt, SR):
                self._calculate_clock_offset(pkt)

    def absolute_timestamp_from_packet(self, packet) -> float:
        """Returns the Unix epoch timestamp for the input packet

        Uses the cached clock offset between the NTP and relative timestamp provided
        by the RTCP packets.
        """
        try:
            return (
                self.relative_timestamp_from_packet(packet)
                + self._relative_to_ntp_clock_offset
            )
        except TypeError:
            # self._relative_to_ntp_clock_offset is still None
            raise _UnknownClockoffsetError(
                "Clock offset between relative and NTP clock is still unknown. "
                "Waiting for first RTCP SR packet..."
            ) from None

    def relative_timestamp_from_packet(self, packet: Any) -> float:
        rtpmap = self.get_rtpmap()
        clock_rate = rtpmap["clockRate"]
        return packet.ts / clock_rate

    def _calculate_clock_offset(self, sr_pkt: Any) -> None:
        # Expected input: aiortsp.rtcp.parser.SR packet which converts the raw NTP
        # timestamp [1] from seconds since 1900 to seconds since 1970 (unix epoch)
        # [1] see https://datatracker.ietf.org/doc/html/rfc3550#section-6.4.1

        self._relative_to_ntp_clock_offset = (
            sr_pkt.ntp - self.relative_timestamp_from_packet(sr_pkt)
        )

    def get_rtpmap(self) -> dict[str, Any]:
        media = self.get_primary_media()
        return media["attributes"]["rtpmap"]

    def get_primary_media(self) -> Any:
        for media in self.session.sdp["medias"]:
            if media["type"] in ["video", "application"]:
                return media
