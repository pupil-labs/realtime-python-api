import asyncio
import contextlib
import typing as T
from collections import deque

import cv2
import numpy as np

# Workaround for https://github.com/opencv/opencv/issues/21952
cv2.imshow("cv/av bug", np.zeros(1))
cv2.destroyAllWindows()

from pupil_labs.realtime_api import (  # noqa
    Device,
    Network,
    receive_eye_events_data,
    receive_video_frames,
)

from pupil_labs.realtime_api.streaming import (
    BlinkEventData,
    FixationEventData,
)


async def main():
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return

    async with Device.from_discovered_device(dev_info) as device:
        print(f"Getting status information from {device}")
        status = await device.get_status()

        sensor_eye_events = status.direct_eye_events_sensor()
        if not sensor_eye_events.connected:
            print(f"Eye events sensor is not connected to {device}")
            return

        sensor_world = status.direct_world_sensor()
        if not sensor_world.connected:
            print(f"Scene camera is not connected to {device}")
            return

        restart_on_disconnect = True

        queue_video = asyncio.Queue()
        queue_eye_events = asyncio.Queue()

        process_video = asyncio.create_task(
            enqueue_sensor_data(
                receive_video_frames(sensor_world.url, run_loop=restart_on_disconnect),
                queue_video,
            )
        )
        process_gaze = asyncio.create_task(
            enqueue_sensor_data(
                receive_eye_events_data(sensor_eye_events.url, run_loop=restart_on_disconnect),
                queue_eye_events
            )
        )
        try:
            await match_and_draw(queue_video, queue_eye_events)
        finally:
            process_video.cancel()
            process_gaze.cancel()


async def enqueue_sensor_data(sensor: T.AsyncIterator, queue: asyncio.Queue) -> None:
    async for datum in sensor:
        try:
            queue.put_nowait((datum.datetime, datum))
        except asyncio.QueueFull:
            print(f"Queue is full, dropping {datum}")


async def match_and_draw(queue_video, queue_eye_events):
    fixation_history = deque(maxlen=5)
    fixation_counter = 0

    blink = None
    blink_counter = 0

    while True:
        video_datetime, video_frame = await get_most_recent_item(queue_video)
        bgr_buffer = video_frame.to_ndarray(format="bgr24")

        while not queue_eye_events.empty():
            _, eye_event = await queue_eye_events.get()
            if isinstance(eye_event, FixationEventData):
                fixation_history.append({
                    'id': fixation_counter,
                    'fixation': eye_event,
                })
                fixation_counter += 1

            elif isinstance(eye_event, BlinkEventData):
                blink = eye_event
                blink_counter += 1

        for fixation_meta in fixation_history:
            fixation_id = fixation_meta['id']
            fixation = fixation_meta['fixation']

            age = (video_frame.timestamp_unix_seconds - fixation.end_time_ns * 1e-9)
            duration = (fixation.end_time_ns - fixation.start_time_ns) * 1e-9

            overlay = bgr_buffer.copy()
            cv2.circle(
                overlay,
                (int(fixation.mean_gaze_x), int(fixation.mean_gaze_y)),
                radius=40 + int(duration * 10),
                color=(255, 32, 32),
                thickness=5,
            )
            cv2.putText(
                overlay,
                str(fixation_id),
                (int(fixation.mean_gaze_x) - 10, int(fixation.mean_gaze_y) + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            alpha = min(max(0, 1.0 - age / 5.0), 1.0)
            cv2.addWeighted(overlay, alpha, bgr_buffer, 1 - alpha, 0, bgr_buffer)

        if blink is not None:
            overlay = bgr_buffer.copy()
            cv2.putText(
                overlay,
                f"Blink {blink_counter}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            age = (video_frame.timestamp_unix_seconds - blink.end_time_ns * 1e-9)
            alpha = min(max(0, 1.0 - age / 5.0), 1.0)
            cv2.addWeighted(overlay, alpha, bgr_buffer, 1 - alpha, 0, bgr_buffer)

        cv2.imshow("Scene camera with eye events", bgr_buffer)
        cv2.waitKey(1)


async def get_most_recent_item(queue):
    item = await queue.get()
    while True:
        try:
            next_item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return item
        else:
            item = next_item


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
