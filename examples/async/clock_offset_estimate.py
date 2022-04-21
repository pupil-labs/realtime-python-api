import argparse
import asyncio
import contextlib
import csv
import datetime
import time
from pprint import pprint as print

from pupil_labs.realtime_api import discover_devices
from pupil_labs.realtime_api.clock_echo import ClockOffsetEstimator, time_ms


def monotonic_ms():
    return time.monotonic_ns() // 1_000_000


def perf_counter_ms():
    return time.perf_counter_ns() // 1_000_000


async def estimate_clockoffset(address, port, clock_fn):
    estimator = ClockOffsetEstimator(address, port=port)
    return await estimator.estimate(
        number_of_measurements=100,
        sleep_between_measurements_seconds=0.01,
        clock_ms=clock_fn,
    )


async def measure_available_devices():
    addrs = sorted([(dev.addresses[0], dev.name) async for dev in discover_devices(10)])
    for addr, name in addrs:
        for clock_fn in (time_ms, monotonic_ms, perf_counter_ms):
            yield addr, name, clock_fn, await estimate_clockoffset(
                addr, port=1337, clock_fn=clock_fn
            )


async def results_of_available_devices():
    now = datetime.datetime.now()
    async for addr, name, clock_fn, result in measure_available_devices():
        rt = result.roundtrip_duration_ms
        os = result.clock_offset_ms
        yield {
            "datetime": now,
            "address": addr,
            "name": name,
            "time_fn": clock_fn.__name__,
            "roundtrip_mean": rt.mean,
            "roundtrip_std": rt.std,
            "roundtrip_median": rt.median,
            "clockoffset_mean": os.mean,
            "clockoffset_std": os.std,
            "clockoffset_median": os.median,
        }


async def main(output, num_measuremnts=10, pause_between_measurements_minutes=5):
    print(
        f"{num_measuremnts} measurements, "
        f"with {pause_between_measurements_minutes} minutes pause in between"
    )
    pause_between_measurements_seconds = pause_between_measurements_minutes * 60
    result = [res async for res in results_of_available_devices()]
    if not result:
        raise RuntimeError("No devices found")
    with open(output, "w") as f:
        print(result)
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)
        for _ in range(num_measuremnts - 1):
            await asyncio.sleep(pause_between_measurements_seconds)
            result = [res async for res in results_of_available_devices()]
            print(result)
            writer.writerows(result)
            f.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output", default="clock-offset.csv", help="Output file"
    )
    parser.add_argument(
        "-n", "--num_measuremnts", default=10, type=int, help="Number of measurements"
    )
    parser.add_argument(
        "-p",
        "--pause",
        default=5,
        type=float,
        help="Pause between measurements, in minutes",
    )
    args = parser.parse_args()
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(
            main(
                output=args.output,
                num_measuremnts=args.num_measuremnts,
                pause_between_measurements_minutes=args.pause,
            )
        )
