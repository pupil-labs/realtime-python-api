.. _simple_examples:

Basic Examples
**************

Code examples that use the :ref:`simple_api`.

.. note::
   The examples require Python 3.7+ to run.

.. _simple_discovery_example:

Find one or more devices
========================

.. literalinclude:: ../../examples/simple/discover_devices.py
   :language: python
   :linenos:

Remote control devices
======================

Get current status
------------------

.. literalinclude:: ../../examples/simple/get_status.py
   :language: python
   :linenos:


Send event
----------

.. literalinclude:: ../../examples/simple/send_event.py
   :language: python
   :emphasize-lines: 12,15
   :linenos:

Start, stop and save, and cancel recordings
-------------------------------------------

.. literalinclude:: ../../examples/simple/start_stop_recordings.py
   :language: python
   :emphasize-lines: 13,20,23
   :linenos:


Streaming
=========

Gaze data
---------

.. literalinclude:: ../../examples/simple/stream_gaze.py
   :language: python
   :emphasize-lines: 12
   :linenos:

Scene camera video
------------------

.. literalinclude:: ../../examples/simple/stream_scene_camera_video.py
   :language: python
   :emphasize-lines: 23,24
   :linenos:

.. _stream_video_with_overlayed_gaze_example_simple:

Scene camera video with overlayed gaze
--------------------------------------

.. literalinclude:: ../../examples/simple/stream_video_with_overlayed_gaze.py
   :language: python
   :emphasize-lines: 25
   :linenos:
