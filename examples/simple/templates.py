import beaupy

from pupil_labs.realtime_api.models import InvalidTemplateAnswersError, TemplateItem
from pupil_labs.realtime_api.simple import discover_one_device

# handle KeyboardInterrupts ourselves
beaupy.Config.raise_on_interrupt = True

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# Fetch current template definition
template = device.get_template()

# Fetch data filled on the template
data = device.get_template_data()

LINE = "\u2500" * 40
RED = "\033[31m"
RESET = "\033[0m"

print(f"[{template.name}] Data pre-filled:")
print(data)


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
    return beaupy.prompt(
        f"Enter value for '{item.title}': ",
        initial_value="" if current_value is None else str(current_value),
    )


# Filling a template
questionnaire = {}
if template:
    try:
        for item in template.items:
            if item.widget_type in ("SECTION_HEADER", "PAGE_BREAK"):
                continue
            print(LINE)
            print(
                f"ID: {item.id} - Title: {item.title} "
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
                else:
                    if item.required:
                        if current_value != [""]:
                            break
                        else:
                            print("This field is required. Please enter a value.")
                            continue
                    if not item.required:
                        break
                    print("This field is required. Please enter a value.")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Skipping the rest of the template")

print(LINE)
# Sending the template
if questionnaire:
    device.post_template(questionnaire)

# Fetch new data filled on the template
data = device.get_template_data()

# Iterate to check filled data
print(f"[{template.name}] Data post:")
print(data)

device.close()
