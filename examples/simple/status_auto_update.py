from pupil_labs.realtime_api.simple import Network

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = Network().wait_for_new_device(timeout_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

scene_camera = device.world_sensor()
connected = False if scene_camera is None else scene_camera.connected
print("Scene camera connected:", connected)

input("(Dis)connect the scene camera and hit enter...")

scene_camera = device.world_sensor()
connected = False if scene_camera is None else scene_camera.connected
print("Scene camera connected:", connected)

device.close()
