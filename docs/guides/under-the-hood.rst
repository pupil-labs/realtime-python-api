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
    The device serves the built-in monitor web app at the document root ``/``. The API
    is served under the ``/api`` path. You can find the full
    `OpenAPI 3 <https://swagger.io/specification/>`_ specification of the REST API
    :ref:`here <openapi_spec>`.

Start/stop/cancel recordings
----------------------------

By sending `HTTP POST <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST>`_
requests to the ``/api/recording:*`` endpoints, you can start, stop, and cancel
recordings.

- :ref:`POST /api/recording:start <openapi_spec>` - Starts a recording if possible
- :ref:`POST /api/recording:stop_and_save <openapi_spec>` - Stops and saves the running
  recording if possible
- :ref:`POST /api/recording:cancel <openapi_spec>` - Stops and discards the running
  recording if possible

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

- :ref:`POST /api/event <openapi_spec>` - Sends an event to the device

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

- :ref:`GET /api/status <openapi_spec>` - Receive status from device

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

RTSP Streaming API
==================

1. High level overview over RTSP, RTP, and RTCP
2. How to get stream entry points from status call
3. Receive gaze
    1. Without timestamps (explain how to decode RTP payload)
    2. With relative timestamps (explain how to get timestamps from RTP headers)
    3. With wall clock timestamps (explain hot to sync relative ts to wall clock ts using RTCP packets)
4. Receive video
    1. Using OpenCV without timestamps
    2. Using PyAV (and reusing  wall clock timestamps from 3.3.3)

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
