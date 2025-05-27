---
hide:
    - feedback
---

--8<-- "README.md:0:9"

## Introduction

Many applications benefit from real-time access to eye tracking data. Think of a gaze interaction app that lets
users control a computer with their eyes, or a research experiment that needs to log
[events](https://docs.pupil-labs.com/neon/data-collection/events/) and eye tracking data in sync for later analysis.
You might also want to start/stop recordings programmatically as part of your custom workflow.
All of this is possible with the [RealTime Network API](https://github.com/pupil-labs/realtime-network-api)—a fast and
reliable way to control and access eye tracking data over your local network, built for developers and researchers.

We’ve created a Python Client library for the [Realtime Network API](https://github.com/pupil-labs/realtime-network-api)
that makes it very easy to use, as it doesn't require a deep understanding of the underlying network communication protocols.

In this documentation, we will orientate you to the client, show you the methods you can use, and example code snippets that
show you how to use them. We also introduce the full API reference, along with some cookbook recipes that reveal the full
power of what's possible.

Head to the [Getting Started](./getting-started) section to start learning how to use this client!

Note: If writing code isn’t your thing and you simply need a tool to monitor and control all your devices in real time, check out [Neon Monitor](https://docs.pupil-labs.com/neon/data-collection/monitor-app/).

!!! question "_Not a Python user?_"

    We offer a [Matlab wrapper](https://github.com/pupil-labs/pl-neon-matlab), a [Unity3D (C#)](https://docs.pupil-labs.com/neon/neon-xr/neon-xr-core-package/) client, or you can always implement your own client.

!!! question "_Using Pupil Core?_"

    This package is designed for use with Pupil Invisible and Neon.
    For Pupil Core, please check out the [Pupil Core Network API](https://docs.pupil-labs.com/core/developer/network-api/).
