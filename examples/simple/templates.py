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


def print_opts(data, template):
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
print_opts(data, template)

# Filling a template
questionnaire = {}
if template:
    try:
        for item in template.items:
            if item.widget_type not in ("SECTION_HEADER", "PAGE_BREAK"):
                print("\u2500" * 40)
                print(
                    f"ID: {item.id} - Title: {item.title} "
                    + f"- Input Type: {item.input_type}"
                )
                if item.widget_type in ["CHECKBOX_LIST", "RADIO_LIST"]:
                    print(f"Choices: {item.choices}")
                for key, value in data.items():
                    if str(item.id) == key:
                        print(
                            "Current value: "
                            + f"{value if value and value != [''] else item.help_text}"
                        )
                while True:
                    user_input = input(f"Enter value for '{item.title}': ")

                    if user_input:
                        input_list = [item.strip() for item in user_input.split(",")]
                        try:
                            errors = template.validate_answers(
                                {str(item.id): input_list}, only_passed=True
                            )
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
                                print("This field is required. Please enter a value.")
                                continue
                        if not item.required:
                            break
                        print("This field is required. Please enter a value.")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Skipping the rest of the template")

print("\u2500" * 40)
# Sending the template
if questionnaire:
    device.post_template(questionnaire)

# Fetch new data filled on the template
data = device.get_template_data()

# Iterate to check filled data
print(f"[{template.name}] Data post:")
print_opts(data, template)

device.close()
