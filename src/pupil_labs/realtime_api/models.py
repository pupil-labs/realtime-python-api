import enum
import json
import logging
from collections.abc import Iterator
from dataclasses import asdict, field
from dataclasses import dataclass as dataclass_python
from datetime import datetime
from functools import partial
from textwrap import indent
from typing import Annotated, Any, ClassVar, Literal, NamedTuple
from uuid import UUID

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    conlist,
    create_model,
)
from pydantic.dataclasses import dataclass as dataclass_pydantic
from pydantic.fields import FieldInfo
from pydantic_core import ErrorDetails

logger = logging.getLogger(__name__)


class APIPath(enum.Enum):
    STATUS = "/status"
    RECORDING_START = "/recording:start"
    RECORDING_STOP_AND_SAVE = "/recording:stop_and_save"
    RECORDING_CANCEL = "/recording:cancel"
    EVENT = "/event"
    CALIBRATION = "/../calibration.bin"
    TEMPLATE_DEFINITION = "/template_def"
    TEMPLATE_DATA = "/template_data"

    def full_address(
        self, address: str, port: int, protocol: str = "http", prefix: str = "/api"
    ) -> str:
        return f"{protocol}://{address}:{port}" + prefix + self.value


class DiscoveredDeviceInfo(NamedTuple):
    name: str
    """Full mDNS service name.
    Follows ``'PI monitor:<phone name>:<hardware id>._http._tcp.local.'`` naming pattern
    """
    server: str
    "e.g. ``'pi.local.'``"
    port: int
    "e.g. `8080`"
    addresses: list[str]
    "e.g. ``['192.168.0.2']``"


class Event(NamedTuple):
    name: str | None
    recording_id: str | None
    timestamp: int  # unix epoch, in nanoseconds

    @classmethod
    def from_dict(cls, dct: dict[str, Any]) -> "Event":
        return cls(
            name=dct.get("name"),
            recording_id=dct.get("recording_id"),
            timestamp=dct["timestamp"],
        )

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp / 1e9)

    def __repr__(self) -> str:
        return (
            f"Event(name={self.name} "
            f"recording_id={self.recording_id} "
            f"timestamp_unix_ns={self.timestamp} "
            f"datetime={self.datetime})"
        )


class Phone(NamedTuple):
    battery_level: int
    battery_state: Literal["OK", "LOW", "CRITICAL"]
    device_id: str
    device_name: str
    ip: str
    memory: int
    memory_state: Literal["OK", "LOW", "CRITICAL"]
    time_echo_port: int | None = None


class Hardware(NamedTuple):
    version: str = "unknown"
    glasses_serial: str = "unknown"
    world_camera_serial: str = "unknown"
    module_serial: str = "unknown"


class NetworkDevice(NamedTuple):
    """Information about devices discovered by the host device, not the client.

    .. note::
        This class represents device information made available via the websocket update
        connection by the host device (exposed via
        :py:meth:`pupil_labs.realtime_api.device.Device.status_updates`). Devices
        discovered directly by this library are represented as
        :py:class:`.DiscoveredDeviceInfo` and returned by
        :py:func:`pupil_labs.realtime_api.discovery.discover_devices` and
        :py:class:`pupil_labs.realtime_api.discovery.Network`.
    """

    ip: str
    device_id: str
    device_name: str
    connected: bool


class Sensor(NamedTuple):
    sensor: str
    conn_type: str
    connected: bool = False
    ip: str | None = None
    params: str | None = None
    port: int | None = None
    protocol: str = "rtsp"
    stream_error: bool = True

    @property
    def url(self) -> str | None:
        if self.connected:
            return f"{self.protocol}://{self.ip}:{self.port}/?{self.params}"
        return None

    class Name(enum.Enum):
        ANY = None
        GAZE = "gaze"
        WORLD = "world"
        IMU = "imu"
        EYES = "eyes"
        EYE_EVENTS = "eye_events"

    class Connection(enum.Enum):
        ANY = None
        WEBSOCKET = "WEBSOCKET"
        DIRECT = "DIRECT"


class Recording(NamedTuple):
    action: str
    id: str
    message: str
    rec_duration_ns: int

    @property
    def rec_duration_seconds(self) -> float:
        return self.rec_duration_ns / 1e9


Component = Phone | Hardware | Sensor | Recording | NetworkDevice | Event
"""Type annotation for :py:class:`Status <.Status>` components."""

ComponentRaw = dict[str, Any]
"""Type annotation for json-parsed responses from the REST and Websocket API."""

_model_class_map: dict[str, type[Component]] = {
    "Phone": Phone,
    "Hardware": Hardware,
    "Sensor": Sensor,
    "Recording": Recording,
    "Event": Event,
    "NetworkDevice": NetworkDevice,
}

TemplateDataFormat = Literal["api", "simple"]


def _init_cls_with_annotated_fields_only(
    cls: type[Component], d: dict[str, Any]
) -> Component:
    return cls(**{attr: d.get(attr) for attr in cls.__annotations__})


class UnknownComponentError(ValueError):
    pass


def parse_component(raw: ComponentRaw) -> Component:
    """Initialize an explicitly modelled representation

    (:py:obj:`pupil_labs.realtime_api.models.Component`) from the json-parsed dictionary
    (:py:obj:`pupil_labs.realtime_api.models.ComponentRaw`) received from the API.

    :raises UnknownComponentError: if the component name cannot be mapped to an
        explicitly modelled class or the contained data does not fit the modelled
        fields.
    """
    model_name = raw["model"]
    data = raw["data"]
    try:
        model_class = _model_class_map[model_name]
        return _init_cls_with_annotated_fields_only(model_class, data)
    except KeyError as err:
        raise UnknownComponentError(
            f"Could not generate component for {model_name} from {data}"
        ) from err


@dataclass_python
class Status:
    "Represents the Companion's full status"

    phone: Phone
    hardware: Hardware
    sensors: list[Sensor]
    recording: Recording | None

    @classmethod
    def from_dict(cls, status_json_result: list[ComponentRaw]) -> "Status":
        phone = None  # always present
        recording = None  # might not be present
        hardware = Hardware()  # won't be present if glasses are not connected
        sensors = []
        for dct in status_json_result:
            try:
                component = parse_component(dct)
            except UnknownComponentError:
                logger.warning(f"Dropping unknown component: {dct}")
                continue
            if isinstance(component, Phone):
                phone = component
            elif isinstance(component, Hardware):
                hardware = component
            elif isinstance(component, Sensor):
                sensors.append(component)
            elif isinstance(component, Recording):
                recording = component
            elif isinstance(component, NetworkDevice):
                pass  # no need to handle NetworkDevice updates here
            else:
                logger.warning(f"Unknown model class: {type(component).__name__}")
        sensors.sort(key=lambda s: (not s.connected, s.conn_type, s.sensor))
        return cls(phone, hardware, sensors, recording)

    def update(self, component: Component) -> None:
        if isinstance(component, Phone):
            self.phone = component
        elif isinstance(component, Hardware):
            self.hardware = component
        elif isinstance(component, Recording):
            self.recording = component
        elif isinstance(component, Sensor):
            for idx, sensor in enumerate(self.sensors):
                if (
                    sensor.sensor == component.sensor
                    and sensor.conn_type == component.conn_type
                ):
                    self.sensors[idx] = component
                    break

    def matching_sensors(
        self, name: Sensor.Name, connection: Sensor.Connection
    ) -> Iterator[Sensor]:
        for sensor in self.sensors:
            if name is not Sensor.Name.ANY and sensor.sensor != name.value:
                continue
            if (
                connection is not Sensor.Connection.ANY
                and sensor.conn_type != connection.value
            ):
                continue
            yield sensor

    def direct_world_sensor(self) -> Sensor | None:
        return next(
            self.matching_sensors(Sensor.Name.WORLD, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.WORLD.value, conn_type=Sensor.Connection.DIRECT.value
            ),
        )

    def direct_gaze_sensor(self) -> Sensor | None:
        return next(
            self.matching_sensors(Sensor.Name.GAZE, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.GAZE.value, conn_type=Sensor.Connection.DIRECT.value
            ),
        )

    def direct_imu_sensor(self) -> Sensor | None:
        return next(
            self.matching_sensors(Sensor.Name.IMU, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.IMU.value, conn_type=Sensor.Connection.DIRECT.value
            ),
        )

    def direct_eyes_sensor(self) -> Sensor | None:
        return next(
            self.matching_sensors(Sensor.Name.EYES, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.EYES.value, conn_type=Sensor.Connection.DIRECT.value
            ),
        )

    def direct_eye_events_sensor(self) -> Sensor | None:
        return next(
            self.matching_sensors(Sensor.Name.EYE_EVENTS, Sensor.Connection.DIRECT),
            Sensor(
                sensor=Sensor.Name.EYE_EVENTS.value,
                conn_type=Sensor.Connection.DIRECT.value,
            ),
        )


TemplateItemWidgetType = Literal[
    "TEXT", "PARAGRAPH", "RADIO_LIST", "CHECKBOX_LIST", "SECTION_HEADER", "PAGE_BREAK"
]
TemplateItemInputType = Literal["any", "integer", "float"]


@dataclass_pydantic(kw_only=True)
class TemplateItem:
    id: UUID
    title: str
    widget_type: TemplateItemWidgetType
    input_type: TemplateItemInputType
    choices: list[str] | None
    help_text: str | None
    required: bool

    def validate_answer(
        self,
        answer: Any,
        template_format: TemplateDataFormat = "simple",
        raise_exception: bool = True,
    ) -> list[ErrorDetails]:
        answers = {
            str(self.id): self._pydantic_validator(template_format=template_format)
        }
        model = create_model(
            f"TemplateItem_{self.id}_Answer",
            **answers,
            __config__=ConfigDict(extra="forbid"),
        )
        errors = []
        try:
            model.__pydantic_validator__.validate_assignment(
                model.model_construct(), str(self.id), answer
            )
        except ValidationError as e:
            errors = e.errors()

        if errors and raise_exception:
            raise InvalidTemplateAnswersError(self, answers, errors)
        return errors

    def _pydantic_validator(
        self, template_format: TemplateDataFormat
    ) -> tuple[type, FieldInfo] | None:
        if self.widget_type in ("SECTION_HEADER", "PAGE_BREAK"):
            return None
        if self.widget_type not in (
            "RADIO_LIST",
            "TEXT",
            "PARAGRAPH",
            "CHECKBOX_LIST",
        ):
            raise ValueError("unknown widget type")

        if template_format == "simple":
            return self._simple_model_validator()
        elif template_format == "api":
            return self._api_model_validator()
        else:
            raise ValueError(f"unknown format, must be one of: {TemplateDataFormat}")

    @property
    def _value_type(self) -> type:
        if self.input_type == "integer":
            return int
        if self.input_type == "float":
            return float
        return str

    def _simple_model_validator(self) -> tuple[type, FieldInfo]:
        field = Field(title=self.title, description=self.help_text)
        answer_input_type = self._value_type
        if self.widget_type in {"RADIO_LIST", "CHECKBOX_LIST"}:
            answer_input_type = Annotated[
                answer_input_type,
                AfterValidator(partial(option_in_allowed_values, allowed=self.choices)),
            ]
            if not self.required:
                field.default_factory = list

            answer_input_type = conlist(
                answer_input_type,
                min_length=1 if self.required else 0,
                max_length=None if self.widget_type == "CHECKBOX_LIST" else 1,
            )
        else:
            if self.required:
                if self.input_type == "any":
                    answer_input_type = Annotated[
                        answer_input_type, StringConstraints(min_length=1)
                    ]
            else:
                answer_input_type = [answer_input_type] | None
                field.default = None

        return (answer_input_type, field)

    def _api_model_validator(self) -> tuple[type, FieldInfo]:
        field = Field(title=self.title, description=self.help_text)
        answer_input_entry_type = self._value_type

        if self.widget_type in {"RADIO_LIST", "CHECKBOX_LIST"}:
            answer_input_entry_type = Annotated[
                answer_input_entry_type,
                AfterValidator(partial(option_in_allowed_values, allowed=self.choices)),
            ]
        else:
            if self.required:
                answer_input_entry_type = Annotated[
                    answer_input_entry_type, BeforeValidator(not_empty)
                ]
            else:
                if answer_input_entry_type in (int, float):
                    answer_input_entry_type = Annotated[
                        answer_input_entry_type | None,
                        BeforeValidator(allow_empty),
                    ]

        if not self.required:
            field.default_factory = lambda: [""]

        answer_input_type = conlist(
            answer_input_entry_type,
            min_length=1 if self.required else 0,
            max_length=None if self.widget_type == "CHECKBOX_LIST" else 1,
        )
        return (answer_input_type, field)


@dataclass_pydantic(kw_only=True)
class Template:
    created_at: datetime
    id: UUID
    name: str
    updated_at: datetime
    recording_name_format: list[str]
    items: list[TemplateItem] = field(default_factory=list)
    label_ids: list[UUID] = field(default_factory=list, metadata={"readonly": True})
    is_default_template: bool = True
    description: str | None = None
    recording_ids: list[UUID] | None = None
    published_at: datetime | None = None
    archived_at: datetime | None = None

    def convert_from_simple_to_api_format(
        self, data: dict[str, Any]
    ) -> dict[str, list[Any]]:
        api_format = {}
        for question_id, value in data.items():
            if value is None:
                value = ""
            if not isinstance(value, list):
                value = [value]

            api_format[question_id] = value
        return api_format

    def convert_from_api_to_simple_format(
        self, data: dict[str, list[str]]
    ) -> dict[str, Any]:
        simple_format = {}
        for question_id, value in data.items():
            question = self.get_question_by_id(question_id)
            if question.widget_type in {"CHECKBOX_LIST", "RADIO_LIST"}:
                if value == [""] and "" not in question.choices:
                    value = []
            else:
                if not value:
                    value = [""]

                value = value[0]
                if question.input_type != "any":
                    value = None if value == "" else question._value_type(value)

            simple_format[question_id] = value
        return simple_format

    def get_question_by_id(self, question_id: str | UUID) -> TemplateItem | None:
        for item in self.items:
            if str(item.id) == str(question_id):
                return item
        return None

    def _create_answer_model(
        self, template_format: TemplateDataFormat
    ) -> type[BaseModel]:
        answer_types = {}
        for question in self.items:
            validator = question._pydantic_validator(template_format=template_format)
            if validator is None:
                continue
            answer_types[f"{question.id}"] = validator

        model = create_model(
            f"Template_{self.id}_Answers",
            **(answer_types),
            __base__=make_template_answer_model_base(self),
        )

        return model

    def validate_answers(
        self,
        answers: dict[str, list[str]],
        raise_exception: bool = True,
        template_format=TemplateDataFormat,
    ) -> list[ErrorDetails]:
        AnswerModel = self._create_answer_model(template_format=template_format)
        errors = []
        try:
            AnswerModel(**answers)
        except ValidationError as e:
            errors = e.errors()

        for error in errors:
            question_id = error["loc"][0]
            question = self.get_question_by_id(question_id)
            if question:
                error["question"] = asdict(question)

        if errors and raise_exception:
            raise InvalidTemplateAnswersError(self, answers, errors)
        return errors


def not_empty(v: str) -> str:
    if not len(v) > 0:
        raise ValueError("value is required")
    return v


def allow_empty(v: str) -> str | None:
    if v == "":
        return None
    return v


def option_in_allowed_values(value: Any, allowed: list[Any]) -> Any:
    if value not in allowed:
        raise ValueError(f"{value!r} is not a valid choice from: {allowed}")
    return value


def make_template_answer_model_base(template_: Template) -> type[BaseModel]:
    class TemplateAnswerModelBase(BaseModel):
        template: ClassVar[Template] = template_
        model_config = ConfigDict(extra="forbid")

        def get(self, item_id: str) -> Any | None:
            return self.__dict__.get(item_id)

        def __repr__(self) -> str:
            args = []
            for item_id, _validator in self.model_fields.items():
                question = self.template.get_question_by_id(item_id)
                infos = map(
                    str,
                    [
                        question.title,
                        question.widget_type,
                        question.input_type,
                        question.choices,
                    ],
                )
                line = (
                    f"    {item_id}={self.__dict__[item_id]!r}, # {' - '.join(infos)}"
                )
                args.append(line)
            args = "\n".join(args)

            return f"Template_{self.template.id}_AnswerModel(\n" + args + "\n)"

        __str__ = __repr__

    return TemplateAnswerModelBase


class InvalidTemplateAnswersError(Exception):
    def __init__(
        self,
        template: Template | TemplateItem,
        answers: dict[str, list[str]],
        errors: list[dict],
    ) -> None:
        self.template = template
        self.errors = errors
        self.answers = answers

    def __str__(self) -> str:
        try:
            error_lines = []
            for error in self.errors:
                error_msg = ""
                error_msg += f"location: {error['loc']}\n"
                error_msg += f"  input: {error['input']}\n"
                error_msg += f"  message: {error['msg']}\n"
                question = error.get("question")
                if question:
                    error_msg += (
                        indent(
                            f"question: {json.dumps(question, indent=4, default=str)}",
                            "  ",
                        )
                        + "\n"
                    )
                error_lines.append(indent(error_msg, "   "))
            error_lines = "\n".join(error_lines)

            name = "?"
            if isinstance(self.template, Template):
                name = self.template.name
            elif isinstance(self.template, TemplateItem):
                name = self.template.title

        except Exception as e:
            return f"InvalidTemplateAnswersError.__str__ error: {e}"
        else:
            return f"{name} ({self.template.id}) validation errors:\n{error_lines}"
