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
            bgr_pixels, frame_datetime = device.receive_scene_video_frame()
            draw_time(bgr_pixels, frame_datetime)
            cv2.imshow("Scene Camera - Press ESC to quit", bgr_pixels)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping...")
        device.close()  # explicitly stop auto-update


def draw_time(frame, time):
    frame_txt_font_name = cv2.FONT_HERSHEY_SIMPLEX
    frame_txt_font_scale = 1.0
    frame_txt_thickness = 1

    # first line: frame index
    frame_txt = str(time)

    cv2.putText(
        frame,
        frame_txt,
        (20, 50),
        frame_txt_font_name,
        frame_txt_font_scale,
        (255, 255, 255),
        thickness=frame_txt_thickness,
        lineType=cv2.LINE_8,
    )


if __name__ == "__main__":
    main()
