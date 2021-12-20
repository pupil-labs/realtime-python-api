Code Examples
*************

Remote Control
==============

Get Current Status
------------------

.. literalinclude:: ../examples/get_status.py
   :language: python
   :emphasize-lines: 4,8-21
   :linenos:

Send Event
----------

.. literalinclude:: ../examples/send_event.py
   :language: python
   :emphasize-lines: 5,9-18
   :linenos:

Start, stop and save, and cancel recordings
-------------------------------------------

.. literalinclude:: ../examples/start_stop_recordings.py
   :language: python
   :emphasize-lines: 4,8-18
   :linenos:

Streaming
=========

Gaze Data
---------

.. literalinclude:: ../examples/stream_gaze.py
   :language: python
   :emphasize-lines: 5,9-17
   :linenos:

Scene Camera Video
------------------

.. literalinclude:: ../examples/stream_scene_camera_video.py
   :language: python
   :emphasize-lines: 7,11-18
   :linenos:

Scene Camera Video With Overlayed Gaze
--------------------------------------

This example processes two streams (video and gaze data) at the same time, matches each
video frame with its temporally closest gaze point, and previews both in a window.

.. literalinclude:: ../examples/stream_video_with_overlayed_gaze.py
   :language: python
   :emphasize-lines: 8,12-41
   :linenos:


Device Discovery
================

.. literalinclude:: ../examples/discover_devices.py
   :language: python
   :emphasize-lines: 5,9-10
   :linenos:
