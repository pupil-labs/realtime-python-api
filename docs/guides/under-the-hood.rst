.. _under_the_hood_guide:

**************
Under The Hood
**************

This guide explains how the Pupil Labs' Realtime API works on the wire and how this
client library abstracts away some of the complexities of the underlying protocols.

.. _http_api:

HTTP REST API
=============

The Pupil Invisible Companion app hosts an `HTTP REST API <https://restfulapi.net/>`_
that can be used to query the phone's current state, remote control it, and look up
information about available data streams.

By default, the API is hosted at `<http://pi.local:8080/>`_. The app will fallback
to a different DNS name and/or port if the default values are taken by another app
already. The current connection details can be looked up under the app's main menu →
Streaming. Alternatively, you can use `Service discovery in the local network`_ to find
available devices.

.. note::
    The device serves the built-in monitor web app (to be released soon!) at the
    document root ``/``. The API is served under the ``/api`` path. You can find the
    full `OpenAPI 3 <https://swagger.io/specification/>`_ specification of the REST API
    `here <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml>`__.

Start/stop/cancel recordings
----------------------------

By sending `HTTP POST <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST>`_
requests to the ``/api/recording:*`` endpoints, you can start, stop, and cancel
recordings.

- `POST /api/recording:start <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L31>`_
  - Starts a recording if possible
- `POST /api/recording:stop_and_save
  <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L47>`_
  - Stops and saves the running recording if possible
- `POST /api/recording:cancel <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L63>`_
  - Stops and discards the running recording if possible

.. attention::
    In specific situations, the app will not comply with the request to start a new
    recording:

    - the selected template has required fields
    - the available storage amount is too low
    - the device battery is too low
    - no wearer has been selected
    - no workspace has been selected
    - the setup bottom sheets have not been completed

.. seealso::
    ``simple`` blocking implementations

    - :py:func:`pupil_labs.realtime_api.simple.Device.recording_start`
    - :py:func:`pupil_labs.realtime_api.simple.Device.recording_stop_and_save`
    - :py:func:`pupil_labs.realtime_api.simple.Device.recording_cancel`

.. seealso::
    Asynchronous implementations

    - :py:func:`pupil_labs.realtime_api.device.Device.recording_start`
    - :py:func:`pupil_labs.realtime_api.device.Device.recording_stop_and_save`
    - :py:func:`pupil_labs.realtime_api.device.Device.recording_cancel`


Send events
-----------

By `HTTP POSTing <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST>`_
requests to the ``/api/event`` endpoint, you can send labeled events to the device.
Events will be timestamped on reception. Alternatively, you can provide a Unix-epoch
timestamp in nanosecond. This is recommended if you want to control the timing of the
event.

- `POST /api/event <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L79>`_
  - Sends an event to the device

.. seealso::
    Implementations

    - ``simple`` blocking: :py:func:`pupil_labs.realtime_api.simple.Device.send_event`
    - Asynchronous: :py:func:`pupil_labs.realtime_api.device.Device.send_event`

Get Current Status
------------------

By sending a `HTTP GET <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET>`_
request to the ``/api/status`` endpoint, you can receive information about the device's
current status. This includes information about the battery and storage capacities,
connected sensors, and running recordings.

- `GET /api/status <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L11>`_
  - Receive status from device

.. seealso::
    Asynchronous implementations
    :py:func:`pupil_labs.realtime_api.device.Device.get_status`

Websocket API
=============

In addition to the :ref:`http_api` above, the Pupil Invisible Companion device also
pushes status updates via a `websocket
<https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API>`_ connection. It is
hosted on the same port as the REST API. By default, you can connect to it via
``ws://pi.local:8080/api/status``.

.. tip::
    You can use this `website <http://livepersoninc.github.io/ws-test-page/>`_ to test
    the websocket connection.

The messages published via this connection have the same format as the `Get Current
Status`_ endpoint.

Streaming API
=============

The Pupil Invisible Companion app uses the RTSP protocol (`RFC 2326
<https://datatracker.ietf.org/doc/html/rfc2326>`_) to stream scene video and gaze data.
Under the hood, communication is three-fold:

- `RTSP`_ (RealTime Streaming Protocol) - Provides meta data about the corresponding stream
- `RTP`_ (Realtime Transport Protocol) - Data delivery channel, contains actual payloads
- `RTCP`_ (RTP Control Protocol) - Provides absolute time information to align multiple streams

The necessary connection information is made available via the `Sensor model
<https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L281>`_
as part of the `Get Current Status`_ and `Websocket API`_.

The RTSP connection URL follows the following pattern::

    rtsp://<ip>:<port>/?<params>

.. caution::
    Each stream is available via two `connection types
    <https://github.com/pupil-labs/realtime-network-api/blob/main/openapi_specification.yaml#L287>`_:

    - ``DIRECT`` - direct RTSP connection, as described in this document
    - ``WEBSOCKET`` - tunneling RTSP over a websocket connection to make it
      available to web browsers

.. seealso::
    The Realtime Network API exposes this information via
    :py:meth:`pupil_labs.realtime_api.models.Status.direct_world_sensor` and
    :py:meth:`pupil_labs.realtime_api.models.Status.direct_gaze_sensor`, returning
    :py:class:`pupil_labs.realtime_api.models.Sensor` instances.

RTSP
----

    The Real Time Streaming Protocol, or RTSP, is an application-level protocol for
    control over the delivery of data with real-time properties.

    Source: https://datatracker.ietf.org/doc/html/rfc2326

Of the various `methods <https://datatracker.ietf.org/doc/html/rfc2326#section-6.1>`_
defined in the RTSP protocol, `SETUP <https://datatracker.ietf.org/doc/html/rfc2326#section-10.4>`_
and `DESCRIBE <https://datatracker.ietf.org/doc/html/rfc2326#section-10.2>`_ are
particularly important for the transmission of the stream's meta and connection
information.

During the SETUP method, client and server exchange information about their
corresponding port numbers for the `RTP`_ and `RTCP`_ connections.

The DESCRIBE response contains `SDP <https://datatracker.ietf.org/doc/html/rfc2326#page-80>`_
(Session Description Protocol) data, describing the following stream attributes (via the
`media's rtpmap <https://datatracker.ietf.org/doc/html/rfc2326#appendix-C.1.3>`_):

- ``encoding`` - The encoding of the stream, e.g. ``H264``
- ``clockRate`` - The clock rate of the stream's relative clock

For video, it also exposes the `sprop-parameter-sets
<https://datatracker.ietf.org/doc/html/rfc6184#section-8.2.1>`_ via its `format-specific
parameters <https://datatracker.ietf.org/doc/html/rfc5576#section-6.3>`_ (``fmtp``).
These contain crucial information in order to initialize the corresponding video decoder.

.. attention::
    Each stream has its own clock rate. For temporal alignment, the clock offset between
    the stream's relative clock and the absolute NTP clock has to be calculated. See
    `RTCP`_ below.

.. seealso::
    To encode gaze data, a custom encoding called ``com.pupillabs.gaze1`` is used.
    You can find more information about it below.

RTP
---

    [The real-time transport protocol] provides end-to-end network transport functions
    suitable for applications transmitting real-time data, such as audio, video or
    simulation data, over multicast or unicast network services. [...] The data
    transport is augmented by a control protocol (`RTCP`_) [...]. `RTP`_ and `RTCP`_ are
    designed to be independent of the underlying transport and network layers.

    Source: https://datatracker.ietf.org/doc/html/rfc3550

Payloads can be split across multiple RTP packets. Their order can be identified via the
packet header's `sequence number <https://datatracker.ietf.org/doc/html/rfc1889#section-5.1>`_.
Packets belonging to the same payload have the same timestamp. The payloads can be
decoded individually. See `Decoding Gaze Data`_ and `Decoding Video Data`_ below.

.. seealso::
    Read more about the RTP timestamp mechanism `here
    <https://datatracker.ietf.org/doc/html/rfc1889#section-5.1>`__.

.. seealso::
    The Realtime Python API exposes raw RTP data via
    :py:func:`pupil_labs.realtime_api.streaming.base.RTSPRawStreamer.receive` and
    calculates relative RTP packet timestamps in
    :py:func:`pupil_labs.realtime_api.streaming.base._WallclockRTSPReader.relative_timestamp_from_packet`.

RTCP
----

The most important role that the RTP control protocol plays for the Pupil Labs Realtime
Network API is to provide timestamps in relative stream time and in absolute NTP time
(`SR RTCP Packet type <https://datatracker.ietf.org/doc/html/rfc1889#section-6.1>`_).

Relative timestamps are calculated by dividing the packet timestamp (numerator) by the
clock rate (denominator), e.g. a timestamp of 250 at a clock rate of 50 Hz corresponds
to ``250 / 50 = 5`` seconds.

    Wallclock time (absolute date and time) is represented using the timestamp format of
    the `Network Time Protocol <https://datatracker.ietf.org/doc/html/rfc1305>`_ (NTP),
    which is in seconds relative to 1 January **1900** 00:00:00 UTC. The full resolution
    NTP timestamp is a 64-bit unsigned fixed-point number with the integer part in the
    first 32 bits and the fractional part in the last 32 bits.

    Source: https://datatracker.ietf.org/doc/html/rfc3550#section-4

Knowing time points in both corresponding clocks, relative and absolute one, allows one
to calculate the clock offset between the two clocks. This is done by subtracting the
one from the other. The offset is then added to new relative timestamps to get the
corresponding time.

.. attention::
    The Realtime Python API converts absolute NTP timestamps to nanoseconds in **Unix**
    epoch (time since 1 January **1970** 00:00:00 UTC). This corresponds to the same
    time base and unit returned by :py:func:`time.time_ns`.

Decoding Gaze Data
------------------

Gaze data is encoded in network byte order (big-endian) and consists of

1. ``x`` - horizontal component of the gaze location in pixels within the scene cameras
   coordinate system. The value is encoded as a 32-bit float.
2. ``y`` - vertical component of the gaze location in pixels within the scene cameras
   coordinate system. The value is encoded as a 32-bit float.
3. ``worn`` - a boolean indicating whether the user is wearing the device. The value is
   encoded as an unsigned 8-bit integer. Currently always set to ``255``.

Each RTP packet contains one gaze datum and has therefore a payload length of 9 bytes.

.. seealso::
    The Realtime Python API exposes gaze data via
    :py:func:`pupil_labs.realtime_api.streaming.gaze.RTSPGazeStreamer.receive` and

Decoding Video Data
-------------------

Video frames are split across multiple RTP packets. The payload is wrapped in the
additional `Network Abstraction Layer <https://datatracker.ietf.org/doc/html/rfc6184#section-5.3>`_
(NAL). This allows finding frame boundaries across fragmented payloads without relying
on the RTP meta information.

Once the data is unpacked from the NAL, it can be passed to a corresponding video
decoder, e.g. :py:meth:`pyav's av.CodecContext <av.codec.context.CodecContext.parse>`.

.. important::
    The video decoder needs to be initialized with the `sprop-parameter-sets
    <https://datatracker.ietf.org/doc/html/rfc6184#section-8.2.1>`_ exposed via the
    `RTSP`_ DESCRIBE method.

.. seealso::
    The Realtime Python API implements the :py:func:`NAL unpacking here
    <pupil_labs.realtime_api.streaming.nal_unit.extract_payload_from_nal_unit>`

Service discovery in the local network
======================================

To avoid having to manually copy the IP address from the Pupil Invisible Companion user
interface, the application announces its REST API endpoint via `multicast DNS service
discovery <https://en.wikipedia.org/wiki/Zero-configuration_networking#DNS-SD_with_multicast>`_.
Specifically, it announces a service of type ``_http._tcp.local.`` and uses the folloing
naming pattern:

.. code-block:: none

    PI monitor:<phone name>:<phone hardware id>._http._tcp.local.

.. seealso::
    The service name is exposed via

    - :py:attr:`pupil_labs.realtime_api.models.DiscoveredDeviceInfo.name` and
    - :py:attr:`pupil_labs.realtime_api.base.DeviceBase.full_name`.

    The phone name component is exposed via

    - :py:attr:`pupil_labs.realtime_api.models.Phone.device_name` and
    - :py:attr:`pupil_labs.realtime_api.simple.Device.phone_name`.

    The phone hardware id component is exposed via

    - :py:attr:`pupil_labs.realtime_api.models.Phone.device_id` and
    - :py:attr:`pupil_labs.realtime_api.simple.Device.phone_id`.

The client's :py:mod:`pupil_labs.realtime_api.discovery` module uses the
:py:mod:`zeroconf` Python package under the hood to discover services.
