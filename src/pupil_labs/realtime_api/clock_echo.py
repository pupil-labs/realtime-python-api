"""Manual clock offset estimation via the Pupil Labs Clock Echo protocol

The Realtime Network API host device timestamps its data with nanoseconds since the
`Unix epoch`_ (January 1, 1970, 00:00:00 UTC). This clock is kept in sync by the
operating system through `NTP`_ (Network Time Protocol). For some use cases, this sync
is not good enough. For more accurate time syncs, the Clock Echo protocol allows the
estimation of the direct offset between the host's and the client's clocks.

.. _Unix epoch: https://docs.python.org/3/library/time.html#epoch
.. _NTP: https://en.wikipedia.org/wiki/Network_Time_Protocol#
   Clock_synchronization_algorithm

The Clock Echo protocol works in the following way:

1. The API host (Pupil Invisible Companion app) opens a TCP server at a specific port
2. The client connects to the host address and port
3. The client sends its current time (``t1``) in milliseconds as an uint64 in network
   byte order to the host
4. The host responds with the clock echo, two uint64 values in network byte order
   1. The first value is equal to the sent client time (``t1``)
   2. The second value corresponds to the host's time in milliseconds (``tH``)
5. The client calculates the duration of steps 3 and 4 (roundtrip time) by measuring the
   client time before sending the request (``t1``) and after receiving the echo (``t2``)
6. The protocol assumes that the transport duration is symmetric. It will assume that
   ``tH`` was measured at the same time as the midpoint betwee ``t1`` and ``t2``.
7. To calculate the offset between the host's and client's clock, we subtract ``tH``
   from the client's midpoint ``(t1 + t2) / 2``::

      offset_ms = ((t1 + t2) / 2) - tH

8. This measurement can be repeated multiple times to make the clock offset estimation
   more robust.

To convert client to host time, subtract the offset::

   host_time_ms = client_time_ms() - offset_ms

This is particularly helpful to accurately timestamp local events, e.g. a stimulus
presentation.

To convert host to client time, add the offset::

   client_time_ms = host_time_ms() + offset_ms

This is particularly helpful to convert the received data into the client's time domain.

----
"""

import asyncio
import collections
import logging
import statistics
import struct
from time import time_ns
from typing import Callable, Iterable, NamedTuple, Optional

logger = logging.getLogger(__name__)

ClockFunction = Callable[[], int]
"""Returns time in milliseconds"""


class ClockEcho(NamedTuple):
    """Measurement of a single clock echo"""

    roundtrip_duration_ms: int
    "Round trip duration of the clock echo, in milliseconds"
    clock_offset_ms: int
    "Clock offset between host and client, in milliseconds"


class Estimate:
    """Provides easy access to statistics over a collection of measurements"""

    def __init__(self, measurements: Iterable[int]) -> None:
        self.measurements = tuple(measurements)
        self._mean = statistics.mean(self.measurements)
        self._std = statistics.stdev(self.measurements)
        self._median = statistics.median(self.measurements)

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def std(self) -> float:
        return self._std

    @property
    def median(self) -> float:
        return self._median

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"#samples={len(self.measurements)}, "
            f"mean±std={self.mean:.3f}±{self._std:.3f}ms, "
            f"median={self.median}ms"
            ")"
        )


class ClockEchoEstimates(NamedTuple):
    """Provides estimates for the roundtrip duration and clock offsets"""

    roundtrip_duration_ms: Estimate
    clock_offset_ms: Estimate


def time_ms():
    """Return milliseconds since `Unix epoch`_ (January 1, 1970, 00:00:00 UTC)"""
    return time_ns() // 1_000_000


class ClockOffsetEstimator:
    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port

    async def estimate(
        self,
        number_of_measurements: int = 100,
        sleep_between_measurements_seconds: Optional[float] = None,
        clock_ms: ClockFunction = time_ms,
    ) -> Optional[ClockEchoEstimates]:
        measurements = collections.defaultdict(list)

        try:
            logger.debug(f"Connecting to {self.address}:{self.port}...")
            reader, writer = await asyncio.open_connection(self.address, self.port)
        except ConnectionError:
            logger.exception(f"Could not connect to Clock Echo server")
            return None

        try:
            rt, offset = await self.request_clock_echo(clock_ms, reader, writer)
            logger.debug(
                f"Dropping first measurement (roundtrip: {rt} ms, offset: {offset} ms)"
            )
            logger.info(f"Measuring {number_of_measurements} times...")
            for _ in range(number_of_measurements):
                try:
                    rt, offset = await self.request_clock_echo(clock_ms, reader, writer)
                    measurements["roundtrip"].append(rt)
                    measurements["offset"].append(offset)
                    if sleep_between_measurements_seconds is not None:
                        await asyncio.sleep(sleep_between_measurements_seconds)
                except ValueError as err:
                    logger.warning(err)
        finally:
            writer.close()
            await writer.wait_closed()
            logger.debug(f"Connection closed {writer.is_closing()}")

        try:
            estimates = ClockEchoEstimates(
                roundtrip_duration_ms=Estimate(measurements["roundtrip"]),
                clock_offset_ms=Estimate(measurements["offset"]),
            )
        except statistics.StatisticsError:
            logger.exception("Not enough valid samples were collected")
            return None

        return estimates

    @staticmethod
    async def request_clock_echo(
        clock_ms: ClockFunction,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> ClockEcho:
        """Request a clock echo, measure the roundtrip time, and estimate the clock
        offset
        """
        before_ms = clock_ms()
        before_ms_bytes = struct.pack("!Q", before_ms)
        writer.write(before_ms_bytes)
        await writer.drain()
        validation_server_ms_bytes = await reader.read(16)
        after_ms = clock_ms()
        if len(validation_server_ms_bytes) != 16:
            raise ValueError(
                "Dropping invalid measurement. Expected response of length 16 "
                f"(got {len(validation_server_ms_bytes)})"
            )
        validation_ms, server_ms = struct.unpack("!QQ", validation_server_ms_bytes)
        logger.debug(
            f"Response: {validation_ms} {server_ms} ({validation_server_ms_bytes!r})"
        )
        if validation_ms != before_ms:
            raise ValueError(
                "Dropping invalid measurement. Expected validation timestamp: "
                f"{before_ms} (got {validation_ms})"
            )
        server_ts_in_client_time_ms = round((before_ms + after_ms) / 2)
        offset_ms = server_ts_in_client_time_ms - server_ms
        return (after_ms - before_ms, offset_ms)
