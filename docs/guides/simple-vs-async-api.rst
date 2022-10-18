.. _simple_vs_async_api_guide:

********************
Simple vs. Async API
********************

The module provides two conceptionally different APIs:

1. The ``async`` interface is using Python's `asyncio`_ in order to implement
   non-blocking asynchronous communication. It provides composable components for each
   feature of the Network API. This means that you need to select and combine the
   functionality for your own needs, e.g. :ref:`stream_video_with_overlayed_gaze_example`.
   The ``async`` functionality is implemented in the top-level
   :ref:`pupil_labs.realtime_api <async_api>` namespace.

2. The ``simple`` interface wraps around the ``async`` one, sacrificing flexibility for
   the sake of ease of use. It tries to anticipate and provide a solution for the most
   common use cases. Note, all ``simple`` API functionality can be found in the
   :py:mod:`pupil_labs.realtime_api.simple` namespace.

.. _asyncio: https://docs.python.org/3/library/asyncio.html

.. caution::
   ``async`` and ``simple`` components are not compatible with each other! Do not mix
   them!

Device Classes
**************

There are three different "Device" classes that one needs to differentiate:

1. | :py:class:`pupil_labs.realtime_api.simple.Device`
   | Easy-to-use class that auto-connects to the Companion device on ``__init__`` to
     request the :ref:`current status <simple_get_status_example>` and to keep it up-to-
     date via the :ref:`Websocket API <simple_auto_update_example>`. The phone's state
     is mirrored and cached in the corresponding attributes. Accessing the attributes is
     instant and does not need to perform a request to the phone. The class initiates
     streaming on demand (:py:meth:`pupil_labs.realtime_api.simple.Device.streaming_start`)
     or when needed (any of the ``simple.Device.receive_*`` methods being called). Can be
     initialised with an explicit IP address and port number. Also, returned by the
     ``pupil_labs.realtime_api.simple.discover_*`` functions.
2. | :py:class:`pupil_labs.realtime_api.models.DiscoveredDeviceInfo`
   | Meta-information about discovered devices, e.g. IP address, port number, etc. Not
     able to initiate any connections on its own. Used to configure the following class:
3. | :py:class:`pupil_labs.realtime_api.device.Device`
   | Does not connect to the Companion device on ``__init__`` - only explicitly on calls
     like :py:meth:`pupil_labs.realtime_api.device.Device.get_status`. Subscription to
     the :py:class:`Websocket API <pupil_labs.realtime_api.device.StatusUpdateNotifier>`,
     :ref:`streaming <streaming_api>`, and :py:mod:`clock offset
     estimation <pupil_labs.realtime_api.time_echo>` are implemented in separate components.
