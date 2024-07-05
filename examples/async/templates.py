import asyncio
import os

import beaupy

from pupil_labs.realtime_api import Device, Network
from pupil_labs.realtime_api.models import InvalidTemplateAnswersError, TemplateItem

LINE = "\u2500" * os.get_terminal_size().columns
RED = "\033[31m"
RESET = "\033[0m"


def prompt_checkbox_answer(item: TemplateItem, current_value):
    ticked = []
    for i, choice in enumerate(item.choices):
        current_value: list
        if choice in (current_value or []):
            current_value.remove(choice)
            ticked.append(i)
    choices = beaupy.select_multiple(
        item.choices,
        ticked_indices=ticked,
    )
    return choices


def prompt_radio_answer(item: TemplateItem, current_value):
    cursor_index = 0
    if current_value and current_value[0] in item.choices:
        cursor_index = item.choices.index(current_value[0])

    choice = beaupy.select(item.choices, cursor_index=cursor_index)
    template_input = []
    if choice is not None:
        template_input = [choice]
    return template_input


def prompt_string_answer(item: TemplateItem, current_value):
    placeholder = item.help_text if item.help_text and item.help_text != [""] else None
    current_value = (
        placeholder if not current_value or current_value == [""] else current_value
    )
    return beaupy.prompt(
        f"Enter value for '{item.title}': ",
        initial_value="" if current_value is None else str(current_value),
    )


async def main():  # noqa: C901
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        # Fetch current template definition
        template = await device.get_template()
        # Fetch data filled on the template
        data = await device.get_template_data(format="simple")

        print(f"[{template.name}] Data pre-filled:")
        print(LINE)
        print("\n".join(f"{k}\t{v}" for k, v in data.items()))

        # Filling a template
        questionnaire = {}
        if template:
            try:
                for item in template.items:
                    if item.widget_type in ("SECTION_HEADER", "PAGE_BREAK"):
                        continue
                    print(LINE)
                    print(
                        f"{'* ' if item.required else ''}"
                        + f"ID: {item.id} - Title: {item.title} "
                        + f"- Input Type: {item.input_type}"
                    )
                    current_value = data.get(str(item.id))
                    while True:
                        question = template.get_question_by_id(item.id)
                        if item.widget_type == "CHECKBOX_LIST":
                            template_input = prompt_checkbox_answer(item, current_value)
                        elif item.widget_type == "RADIO_LIST":
                            template_input = prompt_radio_answer(item, current_value)
                        else:
                            template_input = prompt_string_answer(item, current_value)

                        try:
                            print(template_input)
                            errors = question.validate_answer(template_input)
                            if not errors:
                                questionnaire[str(item.id)] = template_input
                                break
                            else:
                                print(f"Errors: {errors}")
                        except InvalidTemplateAnswersError as e:
                            print(f"{RED}Validation failed for: {template_input}")
                            for error in e.errors:
                                print(f"    {error['msg']}")
                            print(LINE + RESET)
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected. Skipping line.")

        print(LINE)

        # Sending the template
        if questionnaire:
            await device.post_template(questionnaire)

        # Fetch new data filled on the template
        data = await device.get_template_data(format="api")

        # Iterate to check filled data
        print(f"[{template.name}] Data post:")
        print(LINE)
        print("\n".join(f"{k}\t{v}" for k, v in data.items()))


if __name__ == "__main__":
    asyncio.run(main())
