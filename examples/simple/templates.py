import datetime

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


def printOpts(data, template):
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
printOpts(data, template)

# Filling a template
questionnaire = {}
if template:
    for item in template.items:
        if item.widget_type != "SECTION_HEADER":
            # Modifying based on the field's title
            if item.title == "Short answer test":
                questionnaire[str(item.id)] = ["Some more test"]
            # Assuming we have created a component with this title and defined
            # Recording Name in Cloud to use this component, we can programmatically
            # seet the recording name
            elif item.title == "Recording name test":
                questionnaire[str(item.id)] = [
                    f"{str(datetime.datetime.today())}_My_rec_name"
                ]
            # Modifying based on the input's type
            elif item.input_type == int:
                questionnaire[str(item.id)] = ["12345"]
            elif item.input_type == float:
                questionnaire[str(item.id)] = ["123.45"]
            # Modifying based on the widget's type
            elif item.widget_type == "PARAGRAPH":
                questionnaire[str(item.id)] = [
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
                    + "sed do eiusmod tempor incididunt ut labore et dolore "
                    + "magna aliqua. Ut enim ad minim veniam, quis nostrud"
                    + "exercitation ullamco laboris nisi ut aliquip ex"
                ]
            elif item.widget_type == "CHECKBOX_LIST":
                questionnaire[str(item.id)] = ["Option 1", "Option 2"]
            elif item.widget_type == "RADIO_LIST" and not item.required:
                questionnaire[str(item.id)] = ["Option 1"]
            elif item.widget_type == "RADIO_LIST":
                questionnaire[str(item.id)] = ["Yes"]

# Sending the template
device.post_template(questionnaire)

# Fetch new data filled on the template
data = device.get_template_data()

# Iterate to check filled data
print(f"[{template.name}] Data post:")
printOpts(data, template)
