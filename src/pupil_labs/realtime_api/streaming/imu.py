import datetime
import logging
import struct
import typing as T

from .base import RTSPData, RTSPRawStreamer
from .imu_pb2 import ImuPacket

logger = logging.getLogger(__name__)


async def receive_imu_data(url, *args, **kwargs) -> T.AsyncIterator[ImuPacket]:
    async with RTSPImuStreamer(url, *args, **kwargs) as streamer:
        async for datum in streamer.receive():
            yield datum


class RTSPImuStreamer(RTSPRawStreamer):
    async def receive(
        self,
    ) -> T.AsyncIterator[ImuPacket]:
        async for data in super().receive():
            try:
                imu_packet = ImuPacket()
                imu_packet.ParseFromString(data.raw)
                yield imu_packet
            except Exception:
                logger.exception(f"Unable to parse imu data {data}")
                raise
