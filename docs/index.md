---
hide:
    - feedback
---

--8<-- "README.md:0:9"

There are many applications where real-time access to eye tracking data is critical. Think of a gaze interaction app that lets users control a computer with their eyes, or a research experiment that needs to log [events](https://docs.pupil-labs.com/neon/data-collection/events/) and eye tracking data in sync for later analysis.

For example, you might want to launch a screen-based experiment and automatically start recording when the stimulus appears, while also logging timestamps of when the subject interacts with the screen.

This is all possible with the [Real-Time Network API](https://github.com/pupil-labs/realtime-network-api)—a fast, reliable way to access eye tracking data over your local network, built for developers and researchers.

We’ve wrapped it in a Python library that smooths out the rough edges: handling gaze-to-frame matching, device discovery, and providing simple tools to start/stop recordings or log events without needing to understand the underlying network communication.

You also don’t need to be a programming expert. If you’ve ever wanted to build something that reacts to gaze, or need real-time access to any of the device streams, this library makes it easy.

But if writing code isn’t your thing, that’s okay too. [Neon Monitor](https://docs.pupil-labs.com/neon/data-collection/monitor-app/) is a no-code tool designed for live monitoring, starting/ stopping recordings or sending event annotations.

_Not a Python user?_ No problem. We offer a [Matlab wrapper](https://github.com/pupil-labs/pl-neon-matlab), a [Unity](https://docs.pupil-labs.com/neon/neon-xr/neon-xr-core-package/) (C#) client, or you can always talk directly to the API using your own implementation.

## What can I do with it?

Whether you’re building gaze-driven interaction tools, running tightly timed experiments, automating recordings, logging events, or accessing metrics in real-time, this library makes it straightforward.

The library provides a simple interface have a look at the different [methods](./methods/simple.md) available, to learn what you can do with it and examples of how to use them. Need inspiration? Get a look at the cookbook section, which showcases the library being used in different scenarios.

## How do I use it?

Firstly install the library as shown below, and navigate to the [Getting Started](./getting-started.md) section of the documentation and start learning how to use the library.

## Installation

This package is available on PyPI and can be installed using pip:

```
pip install pupil-labs-realtime-api
```

Or, to install directly from the repository:

```bash
pip install -e git+https://github.com/pupil-labs/realtime-python-api.git
```

??? warning "Python Compatibility"

    This package requires Python **3.10** or higher. If you are using an older version of Python, please consider upgrading to a newer one.
    If your project does not allow you to migrate to 3.10+ or you simply want to keep using Python 3.9, you can use the `<2.0` version of this package.

    ```python
    pip install pupil-labs-realtime-api<2.0
    ```

---

!!! failure "Using Pupil Core?"

    This package is designed for use with Pupil Invisible and Neon.
    For Pupil Core, please check out the [Pupil Core Network API](https://docs.pupil-labs.com/core/developer/network-api/).
