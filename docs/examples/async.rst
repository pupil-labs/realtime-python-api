Asynchronous Examples
*********************

.. note::
   The examples require Python 3.7+ to run and use the :py:mod:`asyncio` framework.

Remote Control
==============

.. _get_status_example:

Get Current Status
------------------

.. literalinclude:: ../../examples/async/device_status_get_current.py
   :language: python
   :emphasize-lines: 7,12,13
   :linenos:

Status Updates
--------------

Wait for status updates from the device

.. literalinclude:: ../../examples/async/device_status_update_wait.py
   :language: python
   :emphasize-lines: 15
   :linenos:

Get a callback when there is a new status updates

.. literalinclude:: ../../examples/async/device_status_update_via_callback.py
   :language: python
   :emphasize-lines: 20,21,24
   :linenos:

Send Event
----------

.. literalinclude:: ../../examples/async/send_event.py
   :language: python
   :emphasize-lines: 15,19-21
   :linenos:

Start, stop and save, and cancel recordings
-------------------------------------------

.. literalinclude:: ../../examples/async/start_stop_recordings.py
   :language: python
   :emphasize-lines: 22,26
   :linenos:

Streaming
=========

Gaze Data
---------

.. literalinclude:: ../../examples/async/stream_gaze.py
   :language: python
   :emphasize-lines: 15,21-23
   :linenos:

Scene Camera Video
------------------

.. literalinclude:: ../../examples/async/stream_scene_camera_video.py
   :language: python
   :emphasize-lines: 17,23-25
   :linenos:

.. _stream_video_with_overlayed_gaze_example:

Scene Camera Video With Overlayed Gaze
--------------------------------------

This example processes two streams (video and gaze data) at the same time, matches each
video frame with its temporally closest gaze point, and previews both in a window.

.. literalinclude:: ../../examples/async/stream_video_with_overlayed_gaze.py
   :language: python
   :emphasize-lines: 42,48,69,70
   :linenos:


Device Discovery
================

.. literalinclude:: ../../examples/async/discover_devices.py
   :language: python
   :emphasize-lines: 9,13
   :linenos:
