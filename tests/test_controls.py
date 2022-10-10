from dataclasses import fields

from pupil_labs.realtime_api.camera_control import (
    ChangeRequestParameters,
    Control,
    ControlStateEnum,
    ControlStateEnumResponse,
    ControlStateInteger,
    ControlStateIntegerResponse,
)


def test_all_controls_in_params():
    assert all(
        ctrl.value in ChangeRequestParameters.__optional_keys__ for ctrl in Control
    )


def test_ctrl_states_in_reponse():
    assert all(
        f.name in ControlStateEnumResponse.__required_keys__
        for f in fields(ControlStateEnum)
    )
    assert all(
        f.name in ControlStateIntegerResponse.__required_keys__
        for f in fields(ControlStateInteger)
    )
