import time

from pupil_labs.realtime_api.simple import Network, discover_devices

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...\n\t", end="")
print(Network().wait_for_new_device(timeout_seconds=10.0))

print("---")
# List all devices that could be found within 5 seconds
print("Starting a new 5 second search...\n\t", end="")
print(discover_devices(search_duration_seconds=5.0))

print("---")
print("Start monitoring the network...")
network = Network()

time.sleep(2.0)
print("After 2 seconds:\n\t", end="")
print(network.devices)

time.sleep(3.0)
print("After 5 seconds:\n\t", end="")
print(network.devices)

# It is good practice to explicitly stop searching. Devices referenced outside of the
# network object remain available, e.g. `device = network.devices[0]`
network.close()
