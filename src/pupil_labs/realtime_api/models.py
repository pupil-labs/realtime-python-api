import datetime
import enum
import logging
import typing as T

logger = logging.getLogger(__name__)


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


_model_class_map = {
    "Phone": Phone,
    "Hardware": Hardware,
    "Sensor": Sensor,
}


class Status(T.NamedTuple):
    phone: T.Optional[Phone]
    hardware: T.Optional[Hardware]
    sensors: T.List[Sensor]

    @classmethod
    def from_dict(cls, status_json_result: T.List[T.Dict[str, T.Any]]):
        phone = None  # always present
        hardware = Hardware()  # won't be present if glasses are not connected
        sensors = []
        for dct in status_json_result:
            model_name = dct["model"]
            data = dct["data"]
            try:
                model_class = _model_class_map[model_name]
                model = cls._init_cls_with_annotated_fields_only(model_class, data)
                if issubclass(model_class, Phone):
                    phone = model
                elif issubclass(model_class, Hardware):
                    hardware = model
                elif issubclass(model_class, Sensor):
                    sensors.append(model)
                else:
                    logger.debug(f"Unknown model class: {model_class}")
            except KeyError:
                logger.debug(f"Unknown model: {model_name}")
                continue
        sensors.sort(key=lambda s: (not s.connected, s.conn_type, s.sensor))
        return cls(phone, hardware, sensors)

    @staticmethod
    def _init_cls_with_annotated_fields_only(cls, d: T.Dict[str, T.Any]):
        return cls(**{attr: d[attr] for attr in cls.__annotations__})

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
