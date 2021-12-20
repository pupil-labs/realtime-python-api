***************
Getting Started
***************

Connecting to Pupil Invisible Companion
=======================================

Default DNS name and port number
--------------------------------

In order to communicate with the Pupil Invisible Companion app, one needs to connect to
it. To simplify this step, the app registers a local DNS name (``pi.local`` by default).
This name can be used instead of the phone's IP address.

The entry point for the app's realtime API is hosted by default on port 8080.

.. admonition:: Fallback DNS names and port numbers

    If either the DNS name or port are already in use the app will will use a different
    name, e.g. ```pi-1.local``, or increment the entry point port until it finds a free
    one. To check which name and port are being used, open the Streaming dialogue of
    your app.

.. admonition:: Monitor Web App

    The app hosts a monitor web app at the `same address and port
    <http://pi.local:8080>`_. It previews the scene camera video and overlays the
    correponding gaze point, and allows you to start and stop recordings.

Connecting the client
---------------------

The client connects to Pupil Invisible Companion via the
:py:class:`Control <pupil_labs.realtime_api.control.Control>` class.

.. code-block:: python
    :linenos:

    from pupil_labs.realtime_api import Control

It is initialized using an address (DNS name or IP address) and a port number.

.. code-block:: python
    :linenos:

    async with Control("pi.local", 8080) as control:
        pass

.. note::
    The client library uses the :py:mod:`asyncio` framework. See also the `Async IO in
    Python: A Complete Walkthrough <https://realpython.com/async-io-python/>`_ tutorial.

Getting the app's status
------------------------

To check the current status of the phone, use the
:py:meth:`status <pupil_labs.realtime_api.control.Control.get_status()>` method.

.. code-block:: python
    :linenos:

    async with Control("pi.local", 8080) as control:
        status = await control.get_status()

The method returns a :py:class:`Status <pupil_labs.realtime_api.models.Status>` object.
It can be used to

- see the :py:class:`Phone's <pupil_labs.realtime_api.models.Phone>` current battery and
  storage state, ip address, and more.

- see information about the connected
  :py:class:`glasses <pupil_labs.realtime_api.models.Hardware>`

- get a list of connected :py:class:`sensors <pupil_labs.realtime_api.models.Sensor>`

- get information about the current
  :py:class:`recording <pupil_labs.realtime_api.models.Recording>`


See :ref:`get_status_example` for a full example.