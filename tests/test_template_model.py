# flake8: noqa: E501
from functools import partial

import pytest

from pupil_labs.realtime_api.models import InvalidTemplateAnswersError, Template

template_dict = {
    "id": "5eb9529c-bca1-4fa6-b614-fde6bf96a8e6",
    "is_default_template": False,
    "created_at": "2024-06-24T08:35:36.527503Z",
    "updated_at": "2024-06-24T08:43:25.492875Z",
    "items": [
        {
            "choices": [],
            "help_text": "",
            "id": "f279e7dd-9077-4de1-8327-6a1a79aa039a",
            "input_type": "any",
            "required": False,
            "title": "Section Header",
            "widget_type": "SECTION_HEADER",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "b38a4722-1ad6-470c-af35-ebfe6805646d",
            "input_type": "any",
            "required": False,
            "title": "Page Break",
            "widget_type": "PAGE_BREAK",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "f0c97046-974b-44eb-b00c-50771f9b9200",
            "input_type": "any",
            "required": False,
            "title": "Optional short answer",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "1ebb8823-1e0d-4403-a1bf-c9ac17e312b6",
            "input_type": "any",
            "required": True,
            "title": "Required short answer",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "id": "46ed19f3-ad38-42c8-bfa6-4131e7c72671",
            "input_type": "any",
            "required": False,
            "title": "Short answer text with placeholder",
            "help_text": "Placeholder",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "5c3c39d3-6180-45b8-841c-157e5af42507",
            "input_type": "integer",
            "required": True,
            "title": "Required short answer whole number",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "7afa73a1-3315-42f7-afec-56f25eb3e33c",
            "input_type": "integer",
            "required": False,
            "title": "Optional short answer whole number",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "5130bac2-c823-4d3c-bc5d-ab469602b16c",
            "input_type": "float",
            "required": True,
            "title": "Required short answer number",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "c6ceb33a-f883-4a78-9752-6d9744de6f10",
            "input_type": "float",
            "required": False,
            "title": "Optional short answer number",
            "widget_type": "TEXT",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "41442850-bdb9-4e14-a641-f7a8ad9240b6",
            "input_type": "any",
            "required": True,
            "title": "Required Paragraph",
            "widget_type": "PARAGRAPH",
        },
        {
            "choices": [],
            "help_text": "",
            "id": "6fcdc544-ffe3-4289-85ed-567d52772473",
            "input_type": "any",
            "required": False,
            "title": "Optional paragraph",
            "widget_type": "PARAGRAPH",
        },
        {
            "choices": ["Option 1", "Option 2", "Option 3"],
            "help_text": "",
            "id": "c9b687cd-4bb4-4af6-ae2c-1535b0a4a380",
            "input_type": "any",
            "required": True,
            "title": "Required Checkboxes",
            "widget_type": "CHECKBOX_LIST",
        },
        {
            "choices": ["Option 1", "Option 2", "Option 3"],
            "help_text": "",
            "id": "2feaac75-93a7-4607-9fac-9bce98a901ee",
            "input_type": "any",
            "required": False,
            "title": "Optional Checkboxes",
            "widget_type": "CHECKBOX_LIST",
        },
        {
            "choices": ["Yes", "No"],
            "help_text": "",
            "id": "3b051efa-13a7-4cdb-a6bf-82a569fc9099",
            "input_type": "any",
            "required": True,
            "title": "Required Radiolist",
            "widget_type": "RADIO_LIST",
        },
        {
            "choices": ["Yes", "No"],
            "help_text": "",
            "id": "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e",
            "input_type": "any",
            "required": False,
            "title": "Optional Radiolist",
            "widget_type": "RADIO_LIST",
        },
        {
            "choices": ["Option 1"],
            "help_text": "",
            "id": "174bf92b-c1dd-49da-bf26-b47d1d409ddb",
            "input_type": "any",
            "required": True,
            "title": "Required single choice radio",
            "widget_type": "RADIO_LIST",
        },
        {
            "choices": ["Option 1"],
            "help_text": "",
            "id": "30d144f1-8f85-4f02-80c5-be3ad7fd6291",
            "input_type": "any",
            "required": False,
            "title": "Required single choice radio",
            "widget_type": "RADIO_LIST",
        },
    ],
    "name": "test_template",
    "recording_name_format": ["{answer_from_1ebb8823}"],
}


def test_template_answer_api_format():
    template_def = Template(**template_dict)
    validate_template_answers = partial(template_def.validate_answers, format="api")

    def validate_question_answer(question_id: str):
        return partial(
            template_def.get_question_by_id(question_id).validate_answer, format="api"
        )

    # fmt: off
    good_template_answers = {
        "f0c97046-974b-44eb-b00c-50771f9b9200": [""],  # Optional short answer
        "1ebb8823-1e0d-4403-a1bf-c9ac17e312b6": ["short answer"],  # Required short answer
        "5c3c39d3-6180-45b8-841c-157e5af42507": ["1234"],  # Required short whole number
        "7afa73a1-3315-42f7-afec-56f25eb3e33c": [""],  # Optional short whole number
        "5130bac2-c823-4d3c-bc5d-ab469602b16c": ["23.42"],  # Required short number
        "c6ceb33a-f883-4a78-9752-6d9744de6f10": [""],  # Optional short number
        "41442850-bdb9-4e14-a641-f7a8ad9240b6": ["some long text goes here"],  # Required paragraph
        "6fcdc544-ffe3-4289-85ed-567d52772473": [""],  # Optional paragraph
        "c9b687cd-4bb4-4af6-ae2c-1535b0a4a380": ["Option 1", "Option 2"],  # Required checkbox
        "2feaac75-93a7-4607-9fac-9bce98a901ee": [],  # Optional checkbox
        "3b051efa-13a7-4cdb-a6bf-82a569fc9099": ["Yes"],  # Required radio
        "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e": [],  # Optional radio
        "174bf92b-c1dd-49da-bf26-b47d1d409ddb": ["Option 1"],  # Required radio single choice
        "30d144f1-8f85-4f02-80c5-be3ad7fd6291": [],  # Optional radio single choice
        # '46ed19f3-ad38-42c8-bfa6-4131e7c72671' # intentionally missing as its not required
    }
    # fmt: on
    validate_template_answers(good_template_answers)

    for id, value in good_template_answers.items():
        validate_question_answer(id)(value)

    # fmt: off
    bad_number_answers = {
        "5c3c39d3-6180-45b8-841c-157e5af42507": ["a1234"],  # Required short whole number
        "7afa73a1-3315-42f7-afec-56f25eb3e33c": ["a1234"],  # Optional short whole number
        "5130bac2-c823-4d3c-bc5d-ab469602b16c": ["a23.42"],  # Required short number
        "c6ceb33a-f883-4a78-9752-6d9744de6f10": ["a23.42"],  # Optional short number
    }
    # fmt: on

    for id, value in bad_number_answers.items():
        with pytest.raises(InvalidTemplateAnswersError) as exc:
            validate_question_answer(id)(value)

    with pytest.raises(InvalidTemplateAnswersError) as exc:
        validate_template_answers({**good_template_answers, **bad_number_answers})
        assert len(exc.errors) == 4
        for error in exc.errors:
            assert "unable to parse" in error["msg"]

    # fmt: off
    missing_choice_answers = {
        "c9b687cd-4bb4-4af6-ae2c-1535b0a4a380": ["Not a choice"],  # Required checkbox
        "2feaac75-93a7-4607-9fac-9bce98a901ee": ['Not a choice'],  # Optional checkbox
        "3b051efa-13a7-4cdb-a6bf-82a569fc9099": ["Not a choice"],  # Required radio
        "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e": ["Not a choice"],  # Optional radio
        "174bf92b-c1dd-49da-bf26-b47d1d409ddb": ["Not a choice"],  # Required radio single choice
        "30d144f1-8f85-4f02-80c5-be3ad7fd6291": ["Not a choice"],  # Optional radio single choice
    }
    # fmt: on

    for id, value in missing_choice_answers.items():
        with pytest.raises(InvalidTemplateAnswersError) as exc:
            validate_question_answer(id)(value)

    errors = validate_template_answers(
        {**good_template_answers, **missing_choice_answers}, raise_exception=False
    )
    assert len(errors) == 6
    for error in errors:
        assert "not a valid choice" in error["msg"]

    # fmt: off
    too_many_answers =  {
        "3b051efa-13a7-4cdb-a6bf-82a569fc9099": ["Yes", "No"],  # Required radio
        "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e": ["Yes", "No"],  # Optional radio
        "174bf92b-c1dd-49da-bf26-b47d1d409ddb": ["Option 1", "Option 1"],  # Required radio single choice
        "30d144f1-8f85-4f02-80c5-be3ad7fd6291": ["Option 1", "Option 1"],  # Optional radio single choice
    }
    # fmt: on

    for id, value in too_many_answers.items():
        with pytest.raises(InvalidTemplateAnswersError) as exc:
            validate_question_answer(id)(value)

    errors = validate_template_answers(
        {**good_template_answers, **too_many_answers}, raise_exception=False
    )
    assert len(errors) == 4
    for error in errors:
        assert "should have at most" in error["msg"]


def test_template_answers_simple_format():
    template_def = Template(**template_dict)
    validate_template_answers = partial(template_def.validate_answers, format="simple")

    def validate_question_answer(question_id: str):
        return partial(
            template_def.get_question_by_id(question_id).validate_answer,
            format="simple",
        )

    # fmt: off
    good_template_answers = {
        "f0c97046-974b-44eb-b00c-50771f9b9200": None,  # Optional short answer
        "1ebb8823-1e0d-4403-a1bf-c9ac17e312b6": "short answer",  # Required short answer
        "5c3c39d3-6180-45b8-841c-157e5af42507": 1234,  # Required short whole number
        "7afa73a1-3315-42f7-afec-56f25eb3e33c": None,  # Optional short whole number
        "5130bac2-c823-4d3c-bc5d-ab469602b16c": 23.42,  # Required short number
        "c6ceb33a-f883-4a78-9752-6d9744de6f10": None,  # Optional short number
        "41442850-bdb9-4e14-a641-f7a8ad9240b6": "some long text goes here",  # Required paragraph
        "6fcdc544-ffe3-4289-85ed-567d52772473": None,  # Optional paragraph
        "c9b687cd-4bb4-4af6-ae2c-1535b0a4a380": ["Option 1", "Option 2"],  # Required checkbox
        "2feaac75-93a7-4607-9fac-9bce98a901ee": [],  # Optional checkbox
        "3b051efa-13a7-4cdb-a6bf-82a569fc9099": ["Yes"],  # Required radio
        "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e": [],  # Optional radio
        "174bf92b-c1dd-49da-bf26-b47d1d409ddb": ["Option 1"],  # Required radio single choice
        "30d144f1-8f85-4f02-80c5-be3ad7fd6291": [],  # Optional radio single choice
        # '46ed19f3-ad38-42c8-bfa6-4131e7c72671' # intentionally missing as its not required
    }
    # fmt: on
    validate_template_answers(good_template_answers)

    for id, value in good_template_answers.items():
        validate_question_answer(id)(value)

    # fmt: off
    bad_number_answers =  {
        "5c3c39d3-6180-45b8-841c-157e5af42507": "a1234",  # Required short whole number
        "7afa73a1-3315-42f7-afec-56f25eb3e33c": "a1234",  # Optional short whole number
        "5130bac2-c823-4d3c-bc5d-ab469602b16c": "a23.42",  # Required short number
        "c6ceb33a-f883-4a78-9752-6d9744de6f10": "a23.42",  # Optional short number
    }
    # fmt: on

    for id, value in bad_number_answers.items():
        with pytest.raises(InvalidTemplateAnswersError) as exc:
            validate_question_answer(id)(value)

    with pytest.raises(InvalidTemplateAnswersError) as exc:
        validate_template_answers({**good_template_answers, **bad_number_answers})
        assert len(exc.errors) == 4
        for error in exc.errors:
            assert "unable to parse" in error["msg"]

    # fmt: off
    missing_choice_answers = {
        "c9b687cd-4bb4-4af6-ae2c-1535b0a4a380": ["Not a choice"],  # Required checkbox
        "2feaac75-93a7-4607-9fac-9bce98a901ee": ['Not a choice'],  # Optional checkbox
        "3b051efa-13a7-4cdb-a6bf-82a569fc9099": ["Not a choice"],  # Required radio
        "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e": ["Not a choice"],  # Optional radio
        "174bf92b-c1dd-49da-bf26-b47d1d409ddb": ["Not a choice"],  # Required radio single choice
        "30d144f1-8f85-4f02-80c5-be3ad7fd6291": ["Not a choice"],  # Optional radio single choice
    }
    # fmt: on

    for id, value in missing_choice_answers.items():
        with pytest.raises(InvalidTemplateAnswersError) as exc:
            validate_question_answer(id)(value)

    errors = validate_template_answers(
        {**good_template_answers, **missing_choice_answers}, raise_exception=False
    )
    assert len(errors) == 6
    for error in errors:
        assert "not a valid choice" in error["msg"]

    # fmt: off
    too_many_answers = {
        "3b051efa-13a7-4cdb-a6bf-82a569fc9099": ["Yes", "No"],  # Required radio
        "22e2f30b-3cfb-44b1-83eb-dddef4ac6d9e": ["Yes", "No"],  # Optional radio
        "174bf92b-c1dd-49da-bf26-b47d1d409ddb": ["Option 1", "Option 1"],  # Required radio single choice
        "30d144f1-8f85-4f02-80c5-be3ad7fd6291": ["Option 1", "Option 1"],  # Optional radio single choice
    }
    # fmt: on

    for id, value in too_many_answers.items():
        with pytest.raises(InvalidTemplateAnswersError) as exc:
            validate_question_answer(id)(value)

    errors = validate_template_answers(
        {**good_template_answers, **too_many_answers}, raise_exception=False
    )
    assert len(errors) == 4
    for error in errors:
        assert "should have at most" in error["msg"]
