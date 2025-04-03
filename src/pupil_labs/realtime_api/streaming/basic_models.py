import math

from pydantic import BaseModel
from pydantic.fields import computed_field


class Point(BaseModel):
    """A 2D point representation.

    Attributes:
        x (float): X-coordinate.
        y (float): Y-coordinate.

    """

    x: float
    y: float

    def as_tuple(self) -> tuple[float, float]:
        """Get the point as a tuple of (x, y) coordinates.

        Returns:
            Tuple[float, float]: Point coordinates as (x, y).

        """
        return (self.x, self.y)

    def distance_to(self, other: "Point") -> float:
        """Calculate Euclidean distance to another point.

        Args:
            other: Another point.

        Returns:
            float: Distance between the points.

        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Point3D(BaseModel):
    """A 3D point representation.

    Attributes:
        x (float): X-coordinate.
        y (float): Y-coordinate.
        z (float): Z-coordinate.

    """

    x: float
    y: float
    z: float

    def as_tuple(self) -> tuple[float, float, float]:
        """Get the point as a tuple of (x, y, z) coordinates.

        Returns:
            Tuple[float, float, float]: Point coordinates as (x, y, z).

        """
        return (self.x, self.y, self.z)

    @property
    def xy(self) -> Point:
        """Get the XY projection of this 3D point.

        Returns:
            Point: 2D point with x and y coordinates.

        """
        return Point(x=self.x, y=self.y)

    def distance_to(self, other: "Point3D") -> float:
        """Calculate Euclidean distance to another point in 3D space.

        Args:
            other: Another 3D point.

        Returns:
            float: Distance between the points.

        """
        return math.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )


class Vector3D(Point3D):
    """A 3D vector representation.

    This extends Point3D with vector operations.

    Attributes:
        x (float): X-component.
        y (float): Y-component.
        z (float): Z-component.

    """

    @computed_field
    def magnitude(self) -> float:
        """Calculate the magnitude (length) of the vector.

        Returns:
            float: Vector magnitude.

        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Vector3D":
        """Get a normalized version of this vector (unit vector).

        Returns:
            Vector3D: Normalized vector with magnitude 1.

        """
        mag: float = self.magnitude()
        if mag == 0:
            return Vector3D(x=0, y=0, z=0)
        return Vector3D(x=self.x / mag, y=self.y / mag, z=self.z / mag)

    def dot(self, other: "Vector3D") -> float:
        """Calculate dot product with another vector.

        Args:
            other: Another vector.

        Returns:
            float: Dot product.

        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector3D") -> "Vector3D":
        """Calculate cross product with another vector.

        Args:
            other: Another vector.

        Returns:
            Vector3D: Cross product vector.

        """
        return Vector3D(
            x=self.y * other.z - self.z * other.y,
            y=self.z * other.x - self.x * other.z,
            z=self.x * other.y - self.y * other.x,
        )


class Quaternion(BaseModel):
    """A quaternion representation.

    Attributes:
        x (float): X-component.
        y (float): Y-component.
        z (float): Z-component.
        w (float): W-component.

    """

    x: float
    y: float
    z: float
    w: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        """Get the quaternion as a tuple of (x, y, z, w) components.

        Returns:
            Tuple[float, float, float, float]: Quaternion components as (x, y, z, w).

        """
        return (self.x, self.y, self.z, self.w)

    def conjugate(self) -> "Quaternion":
        """Get the conjugate of this quaternion.

        Returns:
            Quaternion: Conjugate quaternion.

        """
        return Quaternion(x=-self.x, y=-self.y, z=-self.z, w=self.w)
