import abc
import logging
import typing as T

from .models import APIPath, DiscoveredDeviceInfo

DeviceType = T.TypeVar("DeviceType", bound="DeviceBase")
"""
Type annotation for concrete sub-classes of :py:class:`DeviceBase
<pupil_labs.realtime_api.base.DeviceBase>`.
"""


class DeviceBase(abc.ABC):
    """Abstract base class representing Realtime API host devices"""

    def __init__(
        self,
        address: str,
        port: int,
        full_name: T.Optional[str] = None,
        dns_name: T.Optional[str] = None,
        suppress_decoding_warnings: bool = True,
    ):
        self.address: str = address
        """REST API server address"""
        self.port: int = port
        """REST API server port"""
        self.full_name: T.Optional[str] = full_name
        """Full service discovery name"""
        self.dns_name: T.Optional[str] = dns_name
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
        cls: T.Type[DeviceType], device: DiscoveredDeviceInfo
    ) -> DeviceType:
        return cls(
            device.addresses[0],
            device.port,
            full_name=device.name,
            dns_name=device.server,
        )

    @classmethod
    def convert_from(cls: T.Type[DeviceType], other: DeviceType) -> DeviceType:
        return cls(
            other.address,
            other.port,
            full_name=other.full_name,
            dns_name=other.dns_name,
        )
