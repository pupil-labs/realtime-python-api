import asyncio
import contextlib
import time

import cv2

from pupil_labs.realtime_api import Device, Network, receive_video_frames


async def main(preview_frame_rate=30):
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()
        sensor_eyes = status.direct_eyes_sensor()
        if not sensor_eyes.connected:
            print(f"Eyes camera is not connected to {device}")
            return

        restart_on_disconnect = True
        _last_update = time.perf_counter()
        async for frame in receive_video_frames(
            sensor_eyes.url, run_loop=restart_on_disconnect
        ):
            bgr_buffer = frame.bgr_buffer()
            draw_time(bgr_buffer, frame.datetime)
            cv2.imshow("Eye Cameras - Press ESC to quit", bgr_buffer)

            time_since_last_update = time.perf_counter() - _last_update
            if time_since_last_update > 1 / preview_frame_rate:
                if cv2.waitKey(1) & 0xFF == 27:
                    return
                _last_update = time.perf_counter()


def draw_time(frame, time):
    frame_txt_font_name = cv2.FONT_HERSHEY_SIMPLEX
    frame_txt_font_scale = 0.5
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
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
