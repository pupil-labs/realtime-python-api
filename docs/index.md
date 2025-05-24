---
hide:
    - feedback
---

--8<-- "README.md:0:9"

There are many applications where real-time access to gaze data is critical. Think of a gaze interaction app that lets users control a computer with their eyes, or a research experiment that needs to log [events](https://docs.pupil-labs.com/neon/data-collection/events/) and eye tracking data in sync for later analysis.
Consider a scenario where you're running a screen-based experiment. You might need recordings to start automatically when a stimulus appears and to log precise timestamps when a participant interacts with the screen.
All of this is possible with the [Real-Time Network API](https://github.com/pupil-labs/realtime-network-api)—a fast, reliable way to access eye tracking data over your local network, built for developers and researchers.

Here, we’ve wrapped this API in a Python library that smooths out the rough edges, handling gaze-to-frame matching, device discovery, and providing simple tools to start/stop recordings or log events without needing to understand the underlying network communication, so you won’t need to be a programming expert to use it.

But if writing code isn’t your thing, that’s okay too, we got you cover. [Neon Monitor](https://docs.pupil-labs.com/neon/data-collection/monitor-app/) is a no-code tool designed for live monitoring, starting/ stopping recordings or sending event annotations.

!!! question "_Not a Python user?_"

    No problem. We offer a [Matlab wrapper](https://github.com/pupil-labs/pl-neon-matlab), a [Unity3D (C#)](https://docs.pupil-labs.com/neon/neon-xr/neon-xr-core-package/) client, or you can always talk directly to the API using your own implementation.

If you’ve ever wanted to build something that reacts to gaze, or need real-time access to any of the device streams, this library makes it easy.Whether you’re aiming to build gaze-driven interaction tools, running tightly timed experiments, automating recordings, logging events, or accessing metrics in real-time, you are on the right place.

Navigate to the [Quick Start](./getting-started.md) section of the documentation and start learning how to work with this library or have a look at the different [methods](./methods/simple.md) available, and learn what you can do with it along with examples of how to use these.
Need inspiration? Get a look at the cookbook section, which showcases the library being used in different scenarios.

---

!!! failure "Using Pupil Core?"

    This package is designed for use with Pupil Invisible and Neon.
    For Pupil Core, please check out the [Pupil Core Network API](https://docs.pupil-labs.com/core/developer/network-api/).
