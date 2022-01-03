import asyncio
import contextlib
import logging
import typing as T

import cv2

from pupil_labs.realtime_api import Device, receive_gaze_data, receive_video_frames


async def main():
    async with Device("pi.local", 8080) as device:
        logging.info(f"Getting status information from {device}")
        status = await device.get_status()

        sensor_gaze = status.direct_gaze_sensor()
        if not sensor_gaze.connected:
            logging.error(f"Gaze sensor is not connected to {device}")
            return

        sensor_world = status.direct_world_sensor()
        if not sensor_world.connected:
            logging.error(f"Scene camera is not connected to {device}")
            return

        restart_on_disconnect = True

        queue_video = asyncio.Queue()
        queue_gaze = asyncio.Queue()

        await asyncio.gather(
            enqueue_sensor_data(
                receive_video_frames(sensor_world.url, run_loop=restart_on_disconnect),
                queue_video,
            ),
            enqueue_sensor_data(
                receive_gaze_data(sensor_gaze.url, run_loop=restart_on_disconnect),
                queue_gaze,
            ),
            match_and_draw(queue_video, queue_gaze),
        )


async def enqueue_sensor_data(sensor: T.AsyncIterator, queue: asyncio.Queue) -> None:
    async for datum in sensor:
        try:
            queue.put_nowait((datum.datetime, datum))
        except asyncio.QueueFull:
            logging.warning(f"Queue is full, dropping {datum}")


async def match_and_draw(queue_video, queue_gaze):
    while True:
        video_datetime, video_frame = await get_most_recent_item(queue_video)
        _, gaze_datum = await get_closest_item(queue_gaze, video_datetime)

        bgr_buffer = video_frame.to_ndarray(format="bgr24")

        cv2.circle(
            bgr_buffer,
            (int(gaze_datum.x), int(gaze_datum.y)),
            radius=80,
            color=(0, 0, 255),
            thickness=15,
        )

        cv2.imshow("Scene camera with gaze overlay", bgr_buffer)
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


async def get_closest_item(queue, timestamp):
    item_ts, item = await queue.get()
    # assumes monotonically increasing timestamps
    if item_ts > timestamp:
        return item_ts, item
    while True:
        try:
            next_item_ts, next_item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return item_ts, item
        else:
            if next_item_ts > timestamp:
                return next_item_ts, next_item
            item_ts, item = next_item_ts, next_item


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
