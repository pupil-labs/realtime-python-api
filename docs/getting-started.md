This documentation is broadly structured around four key sections, in addition to the Getting Started guide.

The [Simple API](./methods/simple.md) and [Async API](./methods/async.md) sections detail all methods, along with code
examples that show how to use them. We highly recommend reading about the differences between the Simple and Async modes
before you start using the API, but for users just getting started, the Simple API is recommended as it's very easy to
use and also very powerful.

The [API reference](./modules.md) contains a complete overview of each method, parameter, and response. It assumes a certain
level of prior knowledge as it does not include step-by-step explanations or practical examples. Note that we also link
out to this reference from the Simple and Async API sections where appropriate.

If you’re interested in learning about the underlying communication protocols and other technical details,
the [Under the hood](./guides/under-the-hood.md) section is definitely worth checking out!

Finally, we have included a [Cookbook](./cookbook.md), which contains more complicated and concrete use-cases for
implementations that leverage the Realtime API.

## Simple vs Async

The Python client has two modes: [`Simple`][pupil_labs.realtime_api.simple] and [`Async`][pupil_labs.realtime_api], and
it's important to choose which one is right for your use case. The Simple mode is very easy to use and is recommended
to get started with.

The Async interface is more flexible and allows for non-blocking communication, but it is also more complicated to use.

Check out the [Simple vs Async guide](./guides/simple-vs-async-api.md) to better understand the differences between the
two modes.

## Installation

Now that we've got that out of the way, the next step to take is to install the Realtime API. The entire package is
available on PyPI and can be installed with pip using any of the following commands. Alternatively, you can build it
from source.

=== "pip"

    ```sh
    pip install pupil-labs-realtime-api
    ```

=== "pip + git"

    ```sh
    pip install -e git+https://github.com/pupil-labs/realtime-python-api.git
    ```

=== "uv"

    ```sh
    uv pip install -e git+https://github.com/pupil-labs/realtime-python-api.git
    ```
    or start a Python shell with the package ready to use:
    ```sh
    uv run --with pupil-labs-realtime-api python
    ```

!!! warning "Python Compatibility"

    This package requires Python **3.10** or higher. If you are using an older version of Python, please consider upgrading to a newer one.
    If your project does not allow you to migrate to 3.10+ or you simply want to keep using Python 3.9, you can use the `<2.0` version of this package.

    ```python
    pip install pupil-labs-realtime-api<2.0
    ```

## Where to go next

We recommend that you navigate to our complete [Code Examples and Methods](./methods/index.md) section, which details
all functionality of the Simple and Async API, including code examples and descriptions of how to use them.
