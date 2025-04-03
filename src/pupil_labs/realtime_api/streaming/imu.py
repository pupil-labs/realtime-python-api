import datetime
import logging
from collections.abc import AsyncIterator, Callable
from typing import Any, cast

from pydantic import BaseModel, computed_field

from pupil_labs.neon_recording.stream.imu.imu_pb2 import ImuPacket  # type: ignore

from .._utils import deprecated
from .base import RTSPRawStreamer
from .basic_models import Point3D, Quaternion

logger = logging.getLogger(__name__)


class IMUData(BaseModel):
    """Data from the Inertial Measurement Unit (IMU).

    Contains gyroscope, accelerometer, and rotation data from the IMU sensor.

    Attributes:
        gyro_data (Point3D): Gyroscope data in deg/s.
        accel_data (Point3D): Accelerometer data in m/s².
        quaternion (Quaternion): Rotation represented as a quaternion.
        timestamp_unix_seconds (float): Timestamp in seconds since Unix epoch.

    """

    gyro_data: Point3D
    accel_data: Point3D
    quaternion: Quaternion
    timestamp_unix_seconds: float

    class Config:
        frozen = True

    @computed_field
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @computed_field
    def timestamp_unix_ns(self) -> int:
        return int(self.timestamp_unix_seconds * 1e9)

    @property
    @deprecated(
        since="1.4.0",
        removal_in="2.1.0",
        alternative="timestamp_unix_ns",
        message="This property will be removed in a future release.",
    )
    def timestamp_unix_nanoseconds(self) -> Callable[[], int]:
        return self.timestamp_unix_ns

    @classmethod
    def from_proto(cls, imu_packet: Any) -> "IMUData":
        """Create an IMUData instance from a protobuf IMU packet.

        Args:
            imu_packet: Protobuf IMU packet.

        Returns:
            IMUData: Converted IMU data.

        """
        return cls(
            gyro_data=Point3D(
                x=imu_packet.gyroData.x,
                y=imu_packet.gyroData.y,
                z=imu_packet.gyroData.z,
            ),
            accel_data=Point3D(
                x=imu_packet.accelData.x,
                y=imu_packet.accelData.y,
                z=imu_packet.accelData.z,
            ),
            quaternion=Quaternion(
                x=imu_packet.rotVecData.x,
                y=imu_packet.rotVecData.y,
                z=imu_packet.rotVecData.z,
                w=imu_packet.rotVecData.w,
            ),
            timestamp_unix_seconds=imu_packet.tsNs / 1e9,
        )


@deprecated(
    since="1.4.0",
    removal_in="2.1.0",
    alternative="IMUData.from_proto",
    message="This function will be removed in a future release.",
)
def IMUPacket_to_IMUData(imu_packet: Any) -> IMUData:
    """Convert a protobuf IMU packet to an IMUData object.

    Args:
        imu_packet: Protobuf IMU packet.

    Returns:
        IMUData: Converted IMU data.

    """
    gyro_data = Point3D(
        x=imu_packet.gyroData.x,
        y=imu_packet.gyroData.y,
        z=imu_packet.gyroData.z,
    )
    accel_data = Point3D(
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
    """Receive IMU data from an RTSP stream.

    This is a convenience function that creates an RTSPImuStreamer and yields
    parsed IMU data.

    Args:
        url: RTSP URL to connect to.
        *args: Additional positional arguments passed to RTSPImuStreamer.
        **kwargs: Additional keyword arguments passed to RTSPImuStreamer.

    Yields:
        IMUData: Parsed IMU data.

    """
    async with RTSPImuStreamer(url, *args, **kwargs) as streamer:
        assert isinstance(streamer, RTSPImuStreamer)
        async for datum in streamer.receive():
            yield cast(IMUData, datum)


class RTSPImuStreamer(RTSPRawStreamer):
    """Stream and parse IMU data from an RTSP source.

    This class extends RTSPRawStreamer to parse raw RTSP data into structured
    IMU data objects.
    """

    async def receive(  # type: ignore[override]
        self,
    ) -> AsyncIterator[IMUData]:
        """Receive and parse IMU data from the RTSP stream.

        This method parses the raw binary data into IMUData objects by using
        the protobuf deserializer.

        Yields:
            IMUData: Parsed IMU data.

        Raises:
            Exception: If there is an error parsing the IMU data.

        """
        async for data in super().receive():
            try:
                imu_packet = ImuPacket()
                imu_packet.ParseFromString(data.raw)
                imu_data = IMUData.from_proto(imu_packet)
                yield imu_data
            except Exception:
                logger.exception(f"Unable to parse imu data {data}")
                raise
