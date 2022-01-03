import datetime
import enum
import logging
import typing as T

logger = logging.getLogger(__name__)


class APIPath(enum.Enum):
    STATUS = "/status"
    RECORDING_START = "/recording:start"
    RECORDING_STOP_AND_SAVE = "/recording:stop_and_save"
    RECORDING_CANCEL = "/recording:cancel"
    EVENT = "/event"

    def full_address(
        self, address: str, port: int, protocol: str = "http", prefix: str = "/api"
    ) -> str:
        return f"{protocol}://{address}:{port}" + prefix + self.value


class DiscoveredDevice(T.NamedTuple):
    name: str
    server: str
    port: int
    addresses: T.List[str]


class Event(T.NamedTuple):
    recording_id: T.Optional[str]
    timestamp_unix_ns: int

    @classmethod
    def from_dict(cls, dct: T.Dict[str, T.Any]) -> "Event":
        return cls(
            recording_id=dct.get("recording_id", None),
            timestamp_unix_ns=dct.get("timestamp"),
        )

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp_unix_ns / 1e9)

    def __repr__(self) -> str:
        return (
            f"Event(recording_id={self.recording_id} "
            f"timestamp_unix_ns={self.timestamp_unix_ns} "
            f"datetime={self.datetime})"
        )


class Phone(T.NamedTuple):
    battery_level: int
    battery_state: str
    device_id: str
    device_name: str
    ip: str
    memory: int
    memory_state: str


class Hardware(T.NamedTuple):
    version: str = "unknown"
    glasses_serial: str = "unknown"
    world_camera_serial: str = "unknown"


class Sensor(T.NamedTuple):
    sensor: str
    conn_type: str
    connected: bool = False
    ip: T.Optional[str] = None
    params: T.Optional[str] = None
    port: T.Optional[int] = None
    protocol: str = "rtsp"

    @property
    def url(self) -> str:
        if self.connected:
            return f"{self.protocol}://{self.ip}:{self.port}/?{self.params}"

    class Name(enum.Enum):
        ANY = None
        GAZE = "gaze"
        WORLD = "world"

    class Connection(enum.Enum):
        ANY = None
        WEBSOCKET = "WEBSOCKET"
        DIRECT = "DIRECT"


class Recording(T.NamedTuple):
    action: str
    id: str
    message: str
    rec_duration_ns: int

    @property
    def rec_duration_seconds(self) -> float:
        return self.rec_duration_ns / 1e9


Component = T.Union[Phone, Hardware, Sensor, Recording]
ComponentRaw = T.Dict[str, T.Any]

_model_class_map: T.Dict[str, Component] = {
    "Phone": Phone,
    "Hardware": Hardware,
    "Sensor": Sensor,
    "Recording": Recording,
}


def _init_cls_with_annotated_fields_only(cls, d: T.Dict[str, T.Any]):
    return cls(**{attr: d[attr] for attr in cls.__annotations__})


def parse_component(raw: ComponentRaw) -> Component:
    model_name = raw["model"]
    data = raw["data"]
    model_class = _model_class_map[model_name]
    return _init_cls_with_annotated_fields_only(model_class, data)


class Status(T.NamedTuple):
    phone: Phone
    hardware: Hardware
    sensors: T.List[Sensor]
    recording: T.Optional[Recording]

    @classmethod
    def from_dict(cls, status_json_result: T.List[ComponentRaw]) -> "Status":
        phone = None  # always present
        recording = None  # might not be present
        hardware = Hardware()  # won't be present if glasses are not connected
        sensors = []
        for dct in status_json_result:
            try:
                component = parse_component(dct)
            except KeyError:
                logger.debug(f"Unknown component: {component}")
                continue
            if isinstance(component, Phone):
                phone = component
            elif isinstance(component, Hardware):
                hardware = component
            elif isinstance(component, Sensor):
                sensors.append(component)
            elif isinstance(component, Recording):
                recording = component
            else:
                logger.debug(f"Unknown model class: {type(component).__name__}")
        sensors.sort(key=lambda s: (not s.connected, s.conn_type, s.sensor))
        return cls(phone, hardware, sensors, recording)

    def matching_sensors(self, name: Sensor.Name, connection: Sensor.Connection):
        for sensor in self.sensors:
            if name is not Sensor.Name.ANY and sensor.sensor != name.value:
                continue
            if (
                connection is not Sensor.Connection.ANY
                and sensor.conn_type != connection.value
            ):
                continue
            yield sensor

    def direct_world_sensor(self) -> T.Optional[Sensor]:
        return next(
            self.matching_sensors(Sensor.Name.WORLD, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.WORLD.value, conn_type=Sensor.Connection.DIRECT.value
            ),
        )

    def direct_gaze_sensor(self) -> T.Optional[Sensor]:
        return next(
            self.matching_sensors(Sensor.Name.GAZE, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.GAZE.value, conn_type=Sensor.Connection.DIRECT.value
            ),
        )
