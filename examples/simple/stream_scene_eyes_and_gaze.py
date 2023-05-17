import cv2

from pupil_labs.realtime_api.simple import discover_one_device


def main():
    # Look for devices. Returns as soon as it has found the first device.
    print("Looking for the next best device...")
    device = discover_one_device(max_search_duration_seconds=10)
    if device is None:
        print("No device found.")
        raise SystemExit(-1)

    print(f"Connecting to {device}...")

    try:
        while True:
            matched = device.receive_matched_scene_and_eyes_video_frames_and_gaze()
            if not matched:
                print(
                    "Not able to find a match! Note: Pupil Invisible does not support "
                    "streaming eyes video"
                )
                continue

            cv2.circle(
                matched.scene.bgr_pixels,
                (int(matched.gaze.x), int(matched.gaze.y)),
                radius=80,
                color=(0, 0, 255),
                thickness=15,
            )

            # Render eyes video into the scene video
            height, width, _ = matched.eyes.bgr_pixels.shape
            matched.scene.bgr_pixels[:height, :width, :] = matched.eyes.bgr_pixels

            cv2.imshow(
                "Scene camera with eyes and gaze overlay", matched.scene.bgr_pixels
            )
            if cv2.waitKey(1) & 0xFF == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping...")
        device.close()  # explicitly stop auto-update


if __name__ == "__main__":
    main()
