import asyncio

from pupil_labs.realtime_api import Device, Network


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        # Fetch current template definition
        template = await device.get_template()
        # Fetch data filled on the template
        data = await device.get_template_data()

        async def printOpts(data, template):
            """Iterate to see pre-filled data"""
            for key, value in data.items():
                for item in template.items:
                    if str(item.id) == key:
                        print(f"{item.title}: {value}")

        print("Data pre-filled:")
        await printOpts(data, template)

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
        await device.post_template(questionnaire)

        # Fetch new data filled on the template
        data = await device.get_template_data()

        # Iterate to check filled data
        print("Data post:")
        await printOpts(data, template)


if __name__ == "__main__":
    asyncio.run(main())
