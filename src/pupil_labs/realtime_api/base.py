import abc
import typing as T

from .models import APIPath, DiscoveredDevice


class ControlBase(abc.ABC):
    def __init__(
        self,
        address: str,
        port: int,
        full_name: T.Optional[str] = None,
        dns_name: T.Optional[str] = None,
    ):
        self.address = address
        self.port = port
        self.full_name = full_name
        self.dns_name = dns_name

    def api_url(
        self, path: APIPath, protocol: str = "http", prefix: str = "/api"
    ) -> str:
        return path.full_address(
            self.address, self.port, protocol=protocol, prefix=prefix
        )

    def __repr__(self) -> str:
        return f"Control(ip={self.address}, port={self.port}, dns={self.dns_name})"

    @classmethod
    def from_discovered_device(cls, device: DiscoveredDevice) -> "ControlBase":
        return cls(
            device.addresses[0],
            device.port,
            full_name=device.name,
            dns_name=device.server,
        )

    @classmethod
    def convert_from(cls, other: "ControlBase") -> "ControlBase":
        return cls(
            other.address,
            other.port,
            full_name=other.full_name,
            dns_name=other.dns_name,
        )
