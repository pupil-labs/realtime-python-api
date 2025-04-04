import datetime
import logging
from collections.abc import AsyncIterator
from typing import Any, NamedTuple

from pupil_labs.neon_recording.stream.imu.imu_pb2 import ImuPacket

from .base import RTSPRawStreamer

logger = logging.getLogger(__name__)


class Data3D(NamedTuple):
    x: float
    y: float
    z: float


class Quaternion(NamedTuple):
    x: float
    y: float
    z: float
    w: float


class IMUData(NamedTuple):
    gyro_data: Data3D
    accel_data: Data3D
    quaternion: Quaternion
    timestamp_unix_seconds: float

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @property
    def timestamp_unix_ns(self) -> int:
        return int(self.timestamp_unix_seconds * 1e9)

    # For backward compatibility
    @property
    def timestamp_unix_nanoseconds(self) -> int:
        return self.timestamp_unix_ns


def IMUPacket_to_IMUData(imu_packet: ImuPacket) -> IMUData:
    gyro_data = Data3D(
        x=imu_packet.gyroData.x,
        y=imu_packet.gyroData.y,
        z=imu_packet.gyroData.z,
    )
    accel_data = Data3D(
        x=imu_packet.accelData.x,
        y=imu_packet.accelData.y,
        z=imu_packet.accelData.z,
    )
    quaternion = Quaternion(
        x=imu_packet.rotVecData.x,
        y=imu_packet.rotVecData.y,
        z=imu_packet.rotVecData.z,
        w=imu_packet.rotVecData.w,
    )
    imu_data = IMUData(
        gyro_data=gyro_data,
        accel_data=accel_data,
        quaternion=quaternion,
        timestamp_unix_seconds=imu_packet.tsNs / 1e9,
    )
    return imu_data


async def receive_imu_data(
    url: str, *args: Any, **kwargs: Any
) -> AsyncIterator[IMUData]:
    async with RTSPImuStreamer(url, *args, **kwargs) as streamer:
        async for datum in streamer.receive():
            yield datum


class RTSPImuStreamer(RTSPRawStreamer):
    async def receive(
        self,
    ) -> AsyncIterator[IMUData]:
        async for data in super().receive():
            try:
                imu_packet = ImuPacket()
                imu_packet.ParseFromString(data.raw)
                imu_data = IMUPacket_to_IMUData(imu_packet)
                yield imu_data
            except Exception:
                logger.exception(f"Unable to parse imu data {data}")
                raise
