from beaupy import prompt, select, select_multiple

from pupil_labs.realtime_api.models import InvalidTemplateAnswersError
from pupil_labs.realtime_api.simple import discover_one_device

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


print(f"[{template.name}] Data pre-filled:")
print(data)

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
            print(f"Current value: {current_value}")

            while True:
                question = template.get_question_by_id(item.id)
                if item.widget_type == "CHECKBOX_LIST":
                    ticked = []
                    for i, choice in enumerate(item.choices):
                        current_value: list
                        if choice in (current_value or []):
                            current_value.remove(choice)
                            ticked.append(i)
                    choices = select_multiple(
                        item.choices,
                        ticked_indices=ticked,
                    )
                    template_input = choices
                elif item.widget_type == "RADIO_LIST":
                    choice = select(item.choices)
                    template_input = [choice]
                else:
                    template_input = prompt(
                        f"Enter value for '{item.title}': ",
                        initial_value=str(current_value),
                    )

                try:
                    errors = question.validate_answer(template_input)
                    if not errors:
                        questionnaire[str(item.id)] = template_input
                        break
                    else:
                        print(f"Errors: {errors}")
                except InvalidTemplateAnswersError as e:
                    print(f"Validation failed: {e.errors}")
                    print(LINE)
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
