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
    for key, value in data.items():
        for item in template.items:
            if str(item.id) == key:
                print(f"{item.title}: {value}")


print("Data pre-filled:")
printOpts(data, template)

# Filling a template
questionnaire = {}
if template:
    for item in template.items:
        if item.widget_type != "SECTION_HEADER":
            # Modifying based on title
            if item.title == "Text Input":
                questionnaire[str(item.id)] = ["Some more test"]
            elif item.title == "Whole Number":
                questionnaire[str(item.id)] = ["11145"]
            elif item.title == "Paragraph":
                questionnaire[str(item.id)] = [
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
                ]
            elif item.title == "TEST 1":
                questionnaire[str(item.id)] = ["true"]
            elif item.title == "Did you enjoyed? ":
                questionnaire[str(item.id)] = ["No"]

# Sending the template
device.post_template(questionnaire)

# Fetch new data filled on the template
data = device.get_template_data()

# Iterate to check filled data
print("Data post:")
printOpts(data, template)
