import datetime
import logging
import struct
from collections.abc import AsyncIterator
from typing import Any, ClassVar, Protocol

from pydantic import BaseModel, computed_field

from .base import RTSPData, RTSPRawStreamer
from .basic_models import Point, Point3D, Vector3D

logger = logging.getLogger(__name__)


class GazeData(BaseModel):
    """Basic gaze data with position and glasses worn status.

    Represents the 2D gaze point on the scene with a timestamp and
    an indicator of whether the glasses are being worn.

    Attributes:
        point (Point): Gaze point coordinates.
        worn (bool): Whether the glasses are being worn.
        timestamp_unix_seconds (float): Timestamp in seconds since Unix epoch.

    """

    point: Point
    worn: bool
    timestamp_unix_seconds: float

    @property
    def x(self) -> float:
        """Get the x-coordinate of the gaze point.

        Returns:
            float: X-coordinate.

        """
        return self.point.x

    @property
    def y(self) -> float:
        """Get the y-coordinate of the gaze point.

        Returns:
            float: Y-coordinate.

        """
        return self.point.y

    @computed_field
    def datetime(self) -> datetime.datetime:
        """Get the timestamp as a datetime object.

        Returns:
            datetime.datetime: The timestamp converted to a datetime object.

        """
        return datetime.datetime.fromtimestamp(self.timestamp_unix_seconds)

    @computed_field
    def timestamp_unix_ns(self) -> int:
        """Get the timestamp in nanoseconds since Unix epoch.

        Returns:
            int: Timestamp in nanoseconds.

        """
        return int(self.timestamp_unix_seconds * 1e9)

    @classmethod
    def from_raw(cls, data: RTSPData) -> "GazeData":
        """Create a GazeData instance from raw RTSP data.

        Args:
            data: Raw RTSP data packet.

        Returns:
            GazeData: Parsed gaze data.

        """
        x, y, worn = struct.unpack("!ffB", data.raw)
        return cls(
            point=Point(x=x, y=y),
            worn=worn == 255,
            timestamp_unix_seconds=data.timestamp_unix_seconds,
        )


class DualMonocularGazeData(GazeData):
    """Experimental class for dual monocular gaze data.

    Contains separate gaze points for left and right eyes.

    Attributes:
        left (Point): Gaze point for left eye.
        right (Point): Gaze point for right eye.
        worn (bool): Whether the glasses are being worn.
        timestamp_unix_seconds (float): Timestamp in seconds since Unix epoch.

    """

    left: Point
    right: Point

    @classmethod
    def from_raw(cls, data: RTSPData) -> "DualMonocularGazeData":
        """Create a DualMonocularGazeData instance from raw RTSP data.

        Args:
            data: Raw RTSP data packet.

        Returns:
            DualMonocularGazeData: Parsed dual monocular gaze data.

        """
        x1, y1, worn, x2, y2 = struct.unpack("!ffBff", data.raw)

        return cls(
            left=Point(x=x1, y=y1),
            right=Point(x=x2, y=y2),
            point=Point(x=(x1 + x2) / 2, y=(y1 + y2) / 2),
            worn=worn == 255,
            timestamp_unix_seconds=data.timestamp_unix_seconds,
        )


class EyestateGazeData(GazeData):
    """Gaze data with additional eye state information.

    Contains gaze position along with detailed eye state information including
    pupil diameter, eyeball center, and optical axis for both eyes.

    Attributes:
        pupil_diameter_left (float): Diameter of left pupil.
        eyeball_center_left (Point3D): Center of left eyeball in 3D space.
        optical_axis_left (Vector3D): Left eye optical axis as a 3D vector.
        pupil_diameter_right (float): Diameter of right pupil.
        eyeball_center_right (Point3D): Center of right eyeball in 3D space.
        optical_axis_right (Vector3D): Right eye optical axis as a 3D vector.

    """

    pupil_diameter_left: float
    eyeball_center_left: Point3D
    optical_axis_left: Vector3D
    pupil_diameter_right: float
    eyeball_center_right: Point3D
    optical_axis_right: Vector3D

    @classmethod
    def from_raw(cls, data: RTSPData) -> "EyestateGazeData":
        """Create an EyestateGazeData instance from raw RTSP data.

        Args:
            data: Raw RTSP data packet.

        Returns:
            EyestateGazeData: Parsed eye state gaze data.

        """
        (
            x,
            y,
            worn,
            pupil_diameter_left,
            eyeball_center_left_x,
            eyeball_center_left_y,
            eyeball_center_left_z,
            optical_axis_left_x,
            optical_axis_left_y,
            optical_axis_left_z,
            pupil_diam_right,
            eyeball_center_right_x,
            eyeball_center_right_y,
            eyeball_center_right_z,
            optical_axis_right_x,
            optical_axis_right_y,
            optical_axis_right_z,
        ) = struct.unpack("!ffBffffffffffffff", data.raw)
        return cls(
            point=Point(x=x, y=y),
            worn=worn == 255,
            pupil_diameter_left=pupil_diameter_left,
            eyeball_center_left=Point3D(
                x=eyeball_center_left_x,
                y=eyeball_center_left_y,
                z=eyeball_center_left_z,
            ),
            optical_axis_left=Vector3D(
                x=optical_axis_left_x, y=optical_axis_left_y, z=optical_axis_left_z
            ),
            pupil_diameter_right=pupil_diam_right,
            eyeball_center_right=Point3D(
                x=eyeball_center_right_x,
                y=eyeball_center_right_y,
                z=eyeball_center_right_z,
            ),
            optical_axis_right=Vector3D(
                x=optical_axis_right_x, y=optical_axis_right_y, z=optical_axis_right_z
            ),
            timestamp_unix_seconds=data.timestamp_unix_seconds,
        )


class EyestateEyelidGazeData(EyestateGazeData):
    """Gaze data with eye state and eyelid information.

    Contains all information from EyestateGazeData plus additional
    eyelid measurements for both eyes.

    Attributes:
        eyelid_angle_top_left (float): Angle of top eyelid for left eye.
        eyelid_angle_bottom_left (float): Angle of bottom eyelid for left eye.
        eyelid_aperture_left (float): Aperture of left eyelid.
        eyelid_angle_top_right (float): Angle of top eyelid for right eye.
        eyelid_angle_bottom_right (float): Angle of bottom eyelid for right eye.
        eyelid_aperture_right (float): Aperture of right eyelid.

    """

    eyelid_angle_top_left: float
    eyelid_angle_bottom_left: float
    eyelid_aperture_left: float
    eyelid_angle_top_right: float
    eyelid_angle_bottom_right: float
    eyelid_aperture_right: float

    @classmethod
    def from_raw(cls, data: RTSPData) -> "EyestateEyelidGazeData":
        """Create an EyestateEyelidGazeData instance from raw RTSP data.

        Args:
            data: Raw RTSP data packet.

        Returns:
            EyestateEyelidGazeData: Parsed eye state with eyelid gaze data.

        """
        (
            x,
            y,
            worn,
            pupil_diameter_left,
            eyeball_center_left_x,
            eyeball_center_left_y,
            eyeball_center_left_z,
            optical_axis_left_x,
            optical_axis_left_y,
            optical_axis_left_z,
            pupil_diam_right,
            eyeball_center_right_x,
            eyeball_center_right_y,
            eyeball_center_right_z,
            optical_axis_right_x,
            optical_axis_right_y,
            optical_axis_right_z,
            eyelid_angle_top_left,
            eyelid_angle_bottom_left,
            eyelid_aperture_left,
            eyelid_angle_top_right,
            eyelid_angle_bottom_right,
            eyelid_aperture_right,
        ) = struct.unpack("!ffBffffffffffffffffffff", data.raw)
        return cls(
            point=Point(x=x, y=y),
            worn=worn == 255,
            pupil_diameter_left=pupil_diameter_left,
            eyeball_center_left=Point3D(
                x=eyeball_center_left_x,
                y=eyeball_center_left_y,
                z=eyeball_center_left_z,
            ),
            optical_axis_left=Vector3D(
                x=optical_axis_left_x, y=optical_axis_left_y, z=optical_axis_left_z
            ),
            pupil_diameter_right=pupil_diam_right,
            eyeball_center_right=Point3D(
                x=eyeball_center_right_x,
                y=eyeball_center_right_y,
                z=eyeball_center_right_z,
            ),
            optical_axis_right=Vector3D(
                x=optical_axis_right_x, y=optical_axis_right_y, z=optical_axis_right_z
            ),
            eyelid_angle_top_left=eyelid_angle_top_left,
            eyelid_angle_bottom_left=eyelid_angle_bottom_left,
            eyelid_aperture_left=eyelid_aperture_left,
            eyelid_angle_top_right=eyelid_angle_top_right,
            eyelid_angle_bottom_right=eyelid_angle_bottom_right,
            eyelid_aperture_right=eyelid_aperture_right,
            timestamp_unix_seconds=data.timestamp_unix_seconds,
        )


GazeDataType = (
    GazeData | DualMonocularGazeData | EyestateGazeData | EyestateEyelidGazeData
)


class SupportsFromRaw(Protocol):
    @classmethod
    def from_raw(cls, data: RTSPData) -> GazeDataType:  # pragma: no cover
        ...


async def receive_gaze_data(
    url: str, *args: Any, **kwargs: Any
) -> AsyncIterator[GazeDataType]:
    """Receive gaze data from an RTSP stream.

    This is a convenience function that creates an RTSPGazeStreamer and yields
    parsed gaze data.

    Args:
        url: RTSP URL to connect to.
        *args: Additional positional arguments passed to RTSPGazeStreamer.
        **kwargs: Additional keyword arguments passed to RTSPGazeStreamer.

    Yields:
        GazeDataType: Parsed gaze data of various types.

    """
    async with RTSPGazeStreamer(url, *args, **kwargs) as streamer:
        assert isinstance(streamer, RTSPGazeStreamer)
        async for datum in streamer.receive():
            yield datum


class RTSPGazeStreamer(RTSPRawStreamer):
    """Stream and parse gaze data from an RTSP source.

    This class extends RTSPRawStreamer to parse raw RTSP data into structured
    gaze data objects. The specific type of gaze data is determined by the
    length of the raw data packet.

    Call `receive_gaze_data` to get parsed GazeDataType objects.
    Call `receive` (inherited) to get raw RTSPData objects.

    Attributes:
        _data_class_by_raw_len (ClassVar[Dict[int, type[SupportsFromRaw]]]): Mapping
        from raw data length to data class.

    """

    _data_class_by_raw_len: ClassVar[dict[int, type[SupportsFromRaw]]] = {
        9: GazeData,
        17: DualMonocularGazeData,
        65: EyestateGazeData,
        89: EyestateEyelidGazeData,
    }

    async def receive(self) -> AsyncIterator[GazeDataType]:  # type: ignore[override]
        """Receive and parse gaze data from the RTSP stream.

        The type of gaze data object is determined by the length of the
        raw data packet:
        - 9 bytes: GazeData (basic gaze position)
        - 17 bytes: DualMonocularGazeData (left and right eye positions)
        - 65 bytes: EyestateGazeData (gaze with eye state)
        - 89 bytes: EyestateEyelidGazeData (gaze with eye state and eyelid info)

        Yields:
            GazeDataType: Parsed gaze data of various types.

        Raises:
            KeyError: If the data length does not match any known format.
            Exception: If there is an error parsing the gaze data.

        """
        async for data in super().receive():
            try:
                cls = self._data_class_by_raw_len[len(data.raw)]
                parsed_data: GazeDataType = cls.from_raw(data)
                yield parsed_data
            except KeyError:
                logger.exception(f"Raw gaze data has unexpected length: {data}")
                raise
            except Exception:
                logger.exception(f"Unable to parse gaze data {data}")
                raise
