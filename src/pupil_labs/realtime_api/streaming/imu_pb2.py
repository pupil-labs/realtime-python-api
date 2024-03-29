# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: imu.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name="imu.proto",
    package="imuproto",
    syntax="proto3",
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\timu.proto\x12\x08imuproto">\n\tAccelData\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\t\n\x01z\x18\x03 \x01(\x02\x12\x10\n\x08reserved\x18\x04 \x01(\x05"=\n\x08GyroData\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\t\n\x01z\x18\x03 \x01(\x02\x12\x10\n\x08reserved\x18\x04 \x01(\x05"J\n\nRotVecData\x12\t\n\x01w\x18\x01 \x01(\x02\x12\t\n\x01x\x18\x02 \x01(\x02\x12\t\n\x01y\x18\x03 \x01(\x02\x12\t\n\x01z\x18\x04 \x01(\x02\x12\x10\n\x08reserved\x18\x05 \x01(\x02"\x91\x01\n\tImuPacket\x12\x0c\n\x04tsNs\x18\x01 \x01(\x04\x12&\n\taccelData\x18\x02 \x01(\x0b\x32\x13.imuproto.AccelData\x12$\n\x08gyroData\x18\x03 \x01(\x0b\x32\x12.imuproto.GyroData\x12(\n\nrotVecData\x18\x04 \x01(\x0b\x32\x14.imuproto.RotVecDatab\x06proto3',
)


_ACCELDATA = _descriptor.Descriptor(
    name="AccelData",
    full_name="imuproto.AccelData",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="x",
            full_name="imuproto.AccelData.x",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="y",
            full_name="imuproto.AccelData.y",
            index=1,
            number=2,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="z",
            full_name="imuproto.AccelData.z",
            index=2,
            number=3,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="reserved",
            full_name="imuproto.AccelData.reserved",
            index=3,
            number=4,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=23,
    serialized_end=85,
)


_GYRODATA = _descriptor.Descriptor(
    name="GyroData",
    full_name="imuproto.GyroData",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="x",
            full_name="imuproto.GyroData.x",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="y",
            full_name="imuproto.GyroData.y",
            index=1,
            number=2,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="z",
            full_name="imuproto.GyroData.z",
            index=2,
            number=3,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="reserved",
            full_name="imuproto.GyroData.reserved",
            index=3,
            number=4,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=87,
    serialized_end=148,
)


_ROTVECDATA = _descriptor.Descriptor(
    name="RotVecData",
    full_name="imuproto.RotVecData",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="w",
            full_name="imuproto.RotVecData.w",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="x",
            full_name="imuproto.RotVecData.x",
            index=1,
            number=2,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="y",
            full_name="imuproto.RotVecData.y",
            index=2,
            number=3,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="z",
            full_name="imuproto.RotVecData.z",
            index=3,
            number=4,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="reserved",
            full_name="imuproto.RotVecData.reserved",
            index=4,
            number=5,
            type=2,
            cpp_type=6,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=150,
    serialized_end=224,
)


_IMUPACKET = _descriptor.Descriptor(
    name="ImuPacket",
    full_name="imuproto.ImuPacket",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="tsNs",
            full_name="imuproto.ImuPacket.tsNs",
            index=0,
            number=1,
            type=4,
            cpp_type=4,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="accelData",
            full_name="imuproto.ImuPacket.accelData",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="gyroData",
            full_name="imuproto.ImuPacket.gyroData",
            index=2,
            number=3,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="rotVecData",
            full_name="imuproto.ImuPacket.rotVecData",
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=227,
    serialized_end=372,
)

_IMUPACKET.fields_by_name["accelData"].message_type = _ACCELDATA
_IMUPACKET.fields_by_name["gyroData"].message_type = _GYRODATA
_IMUPACKET.fields_by_name["rotVecData"].message_type = _ROTVECDATA
DESCRIPTOR.message_types_by_name["AccelData"] = _ACCELDATA
DESCRIPTOR.message_types_by_name["GyroData"] = _GYRODATA
DESCRIPTOR.message_types_by_name["RotVecData"] = _ROTVECDATA
DESCRIPTOR.message_types_by_name["ImuPacket"] = _IMUPACKET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AccelData = _reflection.GeneratedProtocolMessageType(
    "AccelData",
    (_message.Message,),
    {
        "DESCRIPTOR": _ACCELDATA,
        "__module__": "imu_pb2"
        # @@protoc_insertion_point(class_scope:imuproto.AccelData)
    },
)
_sym_db.RegisterMessage(AccelData)

GyroData = _reflection.GeneratedProtocolMessageType(
    "GyroData",
    (_message.Message,),
    {
        "DESCRIPTOR": _GYRODATA,
        "__module__": "imu_pb2"
        # @@protoc_insertion_point(class_scope:imuproto.GyroData)
    },
)
_sym_db.RegisterMessage(GyroData)

RotVecData = _reflection.GeneratedProtocolMessageType(
    "RotVecData",
    (_message.Message,),
    {
        "DESCRIPTOR": _ROTVECDATA,
        "__module__": "imu_pb2"
        # @@protoc_insertion_point(class_scope:imuproto.RotVecData)
    },
)
_sym_db.RegisterMessage(RotVecData)

ImuPacket = _reflection.GeneratedProtocolMessageType(
    "ImuPacket",
    (_message.Message,),
    {
        "DESCRIPTOR": _IMUPACKET,
        "__module__": "imu_pb2"
        # @@protoc_insertion_point(class_scope:imuproto.ImuPacket)
    },
)
_sym_db.RegisterMessage(ImuPacket)


# @@protoc_insertion_point(module_scope)
