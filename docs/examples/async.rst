Asynchronous Examples
*********************

.. note::
   The examples require Python 3.7+ to run and use the :py:mod:`asyncio` framework.

Remote Control
==============

.. _get_status_example:

Get Current Status
------------------

.. literalinclude:: ../../examples/async/get_status.py
   :language: python
   :emphasize-lines: 4,8-21
   :linenos:

Send Event
----------

.. literalinclude:: ../../examples/async/send_event.py
   :language: python
   :emphasize-lines: 5,9-18
   :linenos:

Start, stop and save, and cancel recordings
-------------------------------------------

.. literalinclude:: ../../examples/async/start_stop_recordings.py
   :language: python
   :emphasize-lines: 4,8-18
   :linenos:

Streaming
=========

Gaze Data
---------

.. literalinclude:: ../../examples/async/stream_gaze.py
   :language: python
   :emphasize-lines: 5,9-17
   :linenos:

Scene Camera Video
------------------

.. literalinclude:: ../../examples/async/stream_scene_camera_video.py
   :language: python
   :emphasize-lines: 7,11-18
   :linenos:

.. _stream_video_with_overlayed_gaze_example:

Scene Camera Video With Overlayed Gaze
--------------------------------------

This example processes two streams (video and gaze data) at the same time, matches each
video frame with its temporally closest gaze point, and previews both in a window.

.. literalinclude:: ../../examples/async/stream_video_with_overlayed_gaze.py
   :language: python
   :emphasize-lines: 8,12-41
   :linenos:


Device Discovery
================

.. literalinclude:: ../../examples/async/discover_devices.py
   :language: python
   :emphasize-lines: 5,9-10
   :linenos: