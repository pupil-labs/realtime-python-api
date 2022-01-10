import logging

import cv2

from pupil_labs.realtime_api.simple import discover_one_device

logging.basicConfig(level=logging.WARNING)
# suppress decoding warnings due to incomplete data transmissions
logging.getLogger("libav.h264").setLevel(logging.CRITICAL)
logging.getLogger("libav.swscaler").setLevel(logging.ERROR)


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
            frame, gaze = device.receive_matched_scene_video_frame_and_gaze()
            cv2.circle(
                frame.bgr_pixels,
                (int(gaze.x), int(gaze.y)),
                radius=80,
                color=(0, 0, 255),
                thickness=15,
            )

            cv2.imshow("Scene camera with gaze overlay", frame.bgr_pixels)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping...")
        device.close()  # explicitly stop auto-update


if __name__ == "__main__":
    main()
