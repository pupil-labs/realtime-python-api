Welcome to the Real-Time Python API Client documentation!

This module comes in two flavours, [async][pupil_labs.realtime_api] and [simple][pupil_labs.realtime_api.simple]. If you are new to it, we recommend you to start with the `simple` interface. The `async` interface is more flexible and allows for non-blocking communication, but it is also more complex to use.

1. The [`async`][pupil_labs.realtime_api] interface is using Python's [asyncio](https://docs.python.org/3/library/asyncio.html) in order to implement non-blocking asynchronous communication.

2. The [`simple`][pupil_labs.realtime_api.simple] interface wraps around the `async` one sacrificing flexibility for the sake of ease of use. The calls made using the simple mode are blocking. If you don't know what any of this means, that's okay! The simple mode suffices for most use-cases and you usually do not need to understand the differences!

To get started with either version, check out our [code examples](./examples/index.md).

If you are still unsure which one to use, and you are familiar with Python's `asyncio`, you can check out the [Simple vs Async guide](./guides/simple-vs-async-api.md) to better understand the differences between the two interfaces.
