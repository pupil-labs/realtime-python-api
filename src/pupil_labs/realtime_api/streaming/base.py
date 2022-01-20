import datetime
import logging
import typing as T

from aiortsp.rtcp.parser import SR
from aiortsp.rtsp.reader import RTSPReader

logger = logging.getLogger(__name__)


class SDPDataNotAvailableError(Exception):
    pass


class RTSPData(T.NamedTuple):
    raw: T.ByteString
    timestamp_unix_seconds: float

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self):
        return int(self.timestamp_unix_seconds * 1e9)


async def receive_raw_rtsp_data(url, *args, **kwargs) -> T.AsyncIterator[RTSPData]:
    async with RTSPRawStreamer(url, *args, **kwargs) as streamer:
        for datum in streamer.receive():
            yield datum


class RTSPRawStreamer:
    """Forwards all arguments to
    `aiortsp.rtsp.reader.RTSPReader
    <https://github.com/marss/aiortsp/blob/master/aiortsp/rtsp/reader.py#L31-L32>`_
    """

    def __init__(self, *args, **kwargs):
        self._reader = _WallclockRTSPReader(*args, **kwargs)
        self._encoding = None

    async def receive(self) -> T.AsyncIterator[RTSPData]:
        async for pkt in self.reader.iter_packets():
            try:
                timestamp_seconds = self.reader.absolute_timestamp_from_packet(pkt)
            except _UnknownClockoffsetError:
                # The absolute timestamp is not known yet.
                # Waiting for the first RTCP SR packet...
                continue
            yield RTSPData(pkt.data, timestamp_seconds)

    @property
    def reader(self):
        return self._reader

    @property
    def encoding(self):
        """:raises pupil_labs.realtime_api.streaming.base.SDPDataNotAvailableError:"""
        if self._encoding is None:
            try:
                attributes = self._reader.session.sdp["medias"][0]["attributes"]
                rtpmap = attributes["rtpmap"]
                self._encoding = rtpmap["encoding"].lower()
            except (IndexError, KeyError) as err:
                raise SDPDataNotAvailableError(
                    f"SDP data is missing {err} field"
                ) from err
        return self._encoding

    async def __aenter__(self, *args, **kwargs):
        await self.reader.__aenter__(*args, **kwargs)
        return self

    async def __aexit__(self, *args, **kwargs):
        return await self.reader.__aexit__(*args, **kwargs)


class _UnknownClockoffsetError(Exception):
    pass


class _WallclockRTSPReader(RTSPReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._relative_to_ntp_clock_offset = None

    def handle_rtcp(self, rtcp):
        for pkt in rtcp.packets:
            if isinstance(pkt, SR):
                self._calculate_clock_offset(pkt)

    def absolute_timestamp_from_packet(self, packet):
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
            )

    def relative_timestamp_from_packet(self, packet):
        rtpmap = self.session.sdp["medias"][0]["attributes"]["rtpmap"]
        clock_rate = rtpmap["clockRate"]
        return packet.ts / clock_rate

    def _calculate_clock_offset(self, sr_pkt):
        # Expected input: aiortsp.rtcp.parser.SR packet which converts the raw NTP
        # timestamp [1] from seconds since 1900 to seconds since 1970 (unix epoch)
        # [1] see https://datatracker.ietf.org/doc/html/rfc3550#section-6.4.1

        self._relative_to_ntp_clock_offset = (
            sr_pkt.ntp - self.relative_timestamp_from_packet(sr_pkt)
        )
