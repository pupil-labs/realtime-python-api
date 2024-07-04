import asyncio

import aioconsole

from pupil_labs.realtime_api import Device, Network
from pupil_labs.realtime_api.models import InvalidTemplateAnswersError


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
        data = await device.get_template_data(format="api")

        async def print_opts(data, template):
            """Iterate to see pre-filled data"""
            if not data:
                print("Template is empty.")
                return
            print("\u2500" * 40)
            for key, value in data.items():
                for item in template.items:
                    if str(item.id) == key:
                        print(f"{item.title}: {value} - {item.help_text}")
            print("\u2500" * 40)

        print(f"[{template.name}] Data pre-filled:")
        await print_opts(data, template)

        # Filling a template
        questionnaire = {}
        if template:
            try:
                for item in template.items:
                    if item.widget_type not in ("SECTION_HEADER", "PAGE_BREAK"):
                        print("\u2500" * 40)
                        print(
                            f"ID: {item.id} - Title: {item.title}"
                            + "- Input Type: {item.input_type}"
                        )
                        if item.widget_type in ["CHECKBOX_LIST", "RADIO_LIST"]:
                            print(f"Choices: {item.choices}")
                        for key, value in data.items():
                            if str(item.id) == key:
                                if not value or value == [""]:
                                    if item.help_text and item.help_text != [""]:
                                        value = item.help_text
                                    else:
                                        value = None
                                print(f"Current value: {value}")
                        while True:
                            user_input = await aioconsole.ainput(
                                f"Enter value for '{item.title}': "
                            )

                            if user_input:
                                input_list = [
                                    item.strip() for item in user_input.split(",")
                                ]
                                try:
                                    errors = template.get_question_by_id(
                                        item.id
                                    ).validate_answer(input_list, format="api")
                                    if not errors:
                                        questionnaire[str(item.id)] = input_list
                                        break
                                    else:
                                        print(f"Errors: {errors}")
                                except InvalidTemplateAnswersError as e:
                                    print(f"Validation failed: {e.errors}")
                                    print("\u2500" * 40)
                            else:
                                if item.required:
                                    if value != [""]:
                                        break
                                    else:
                                        print(
                                            "This field is required."
                                            + "Please enter a value."
                                        )
                                        continue
                                if not item.required:
                                    break
                                print("This field is required. Please enter a value.")
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected. Async task stopped.")

        print("\u2500" * 40)

        # Sending the template
        if questionnaire:
            await device.post_template(questionnaire)

        # Fetch new data filled on the template
        data = await device.get_template_data(format="api")

        # Iterate to check filled data
        print(f"[{template.name}] Data pre-filled:")
        await print_opts(data, template)


if __name__ == "__main__":
    asyncio.run(main())
