import abc
import logging
from typing import TypeVar

from .models import APIPath, DiscoveredDeviceInfo

DeviceType = TypeVar("DeviceType", bound="DeviceBase")
"""
Type annotation for concrete sub-classes of :py:class:`DeviceBase
<pupil_labs.realtime_api.base.DeviceBase>`.
"""
T = TypeVar("T", bound="DeviceBase")


class DeviceBase(abc.ABC):  # noqa: B024
    """Abstract base class representing Realtime API host devices"""

    def __init__(
        self,
        address: str,
        port: int,
        full_name: str | None = None,
        dns_name: str | None = None,
        suppress_decoding_warnings: bool = True,
    ):
        self.address: str = address
        """REST API server address"""
        self.port: int = port
        """REST API server port"""
        self.full_name: str | None = full_name
        """Full service discovery name"""
        self.dns_name: str | None = dns_name
        """REST API server DNS name, e.g. ``pi.local.``"""
        if suppress_decoding_warnings:
            # suppress decoding warnings due to incomplete data transmissions
            logging.getLogger("libav.h264").setLevel(logging.CRITICAL)
            logging.getLogger("libav.swscaler").setLevel(logging.ERROR)

    def api_url(
        self, path: APIPath, protocol: str = "http", prefix: str = "/api"
    ) -> str:
        return path.full_address(
            self.address, self.port, protocol=protocol, prefix=prefix
        )

    def __repr__(self) -> str:
        return f"Device(ip={self.address}, port={self.port}, dns={self.dns_name})"

    @classmethod
    def from_discovered_device(
        cls: type[DeviceType], device: DiscoveredDeviceInfo
    ) -> DeviceType:
        return cls(
            device.addresses[0],
            device.port,
            full_name=device.name,
            dns_name=device.server,
        )

    @classmethod
    def convert_from(cls: type[DeviceType], other: T) -> DeviceType:
        return cls(
            other.address,
            other.port,
            full_name=other.full_name,
            dns_name=other.dns_name,
        )
