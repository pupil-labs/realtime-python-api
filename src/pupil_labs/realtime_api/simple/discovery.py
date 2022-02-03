import logging
import queue
import time
import types
import typing as T

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

from ..discovery import is_valid_service_name
from ..models import DiscoveredDeviceInfo
from .device import Device

logger = logging.getLogger(__name__)


def discover_devices(search_duration_seconds: float) -> T.List[Device]:
    """Return all devices that could be found in the given search duration.

    .. seealso::
        The asynchronous equivalent
        :py:class:`pupil_labs.realtime_api.discovery.discover_devices`
    """
    with Network() as network:
        time.sleep(search_duration_seconds)
        return network.devices


class Network:
    """
    .. seealso::
        The asynchronous equivalent
        :py:class:`pupil_labs.realtime_api.discovery.Network`
    """

    def __init__(self) -> None:
        self._devices = {}
        self._new_devices = queue.Queue()
        self._zeroconf = Zeroconf()
        self._browser = ServiceBrowser(
            self._zeroconf, "_http._tcp.local.", handlers=[self._handle_service_change]
        )
        self._open = True

    def __del__(self):
        self.close()

    def close(self):
        if self._open:
            self._browser.cancel()
            self._zeroconf.close()
            self._devices.clear()
            while True:
                try:
                    self._new_devices.get_nowait()
                except queue.Empty:
                    break
            self._devices = None
            self._browser = None
            self._zeroconf = None
            self._open = False

    @property
    def devices(self) -> T.Tuple[Device, ...]:
        return tuple(self._devices.values())

    def wait_for_new_device(
        self, timeout_seconds: T.Optional[float] = None
    ) -> T.Optional[DiscoveredDeviceInfo]:
        try:
            return self._new_devices.get(timeout=timeout_seconds)
        except queue.Empty:
            return None

    def _handle_service_change(
        self,
        zeroconf: Zeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        logger.debug(f"{state_change} {name}")
        if is_valid_service_name(name) and state_change in (
            ServiceStateChange.Added,
            ServiceStateChange.Updated,
        ):
            info = zeroconf.get_service_info(service_type, name, timeout=3000)
            address = '.'.join([str(symbol) for symbol in info.addresses[0]])
            device = Device(
                address,
                info.port,
                full_name=name,
                dns_name=info.server,
            )
            self._devices[name] = device
            self._new_devices.put(device)

        elif name in self._devices:
            del self._devices[name]

    def __enter__(self) -> "Network":
        return self

    def __exit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[types.TracebackType],
    ) -> None:
        self.close()
