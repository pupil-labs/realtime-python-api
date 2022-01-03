import asyncio
import contextlib
import logging

import cv2

from pupil_labs.realtime_api import Device, receive_video_frames


async def main():
    async with Device("pi.local", 8080) as control:
        status = await control.get_status()
        sensor_world = status.direct_world_sensor()
        if not sensor_world.connected:
            logging.error(f"Scene camera is not connected to {control}")
            return

        restart_on_disconnect = True
        async for frame in receive_video_frames(
            sensor_world.url, run_loop=restart_on_disconnect
        ):
            bgr_buffer = frame.bgr_buffer()
            draw_time(bgr_buffer, frame.datetime)
            cv2.imshow("Scene Camera - Press ESC to quit", bgr_buffer)
            if cv2.waitKey(1) & 0xFF == 27:
                return


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
    logging.basicConfig(level=logging.INFO)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
