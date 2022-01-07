.. _basic_examples:

Basic Examples
**************

Code examples that use the :ref:`basic_api`.

.. note::
   The examples require Python 3.7+ to run.

.. _basic_discovery_example:

Find one or more devices
========================

.. literalinclude:: ../../examples/basic/discover_devices.py
   :language: python
   :linenos:

Remote control devices
======================

Get current status
------------------

.. literalinclude:: ../../examples/basic/get_status.py
   :language: python
   :linenos:


Send event
----------

.. literalinclude:: ../../examples/basic/send_event.py
   :language: python
   :emphasize-lines: 12,15
   :linenos:

Start, stop and save, and cancel recordings
-------------------------------------------

.. literalinclude:: ../../examples/basic/start_stop_recordings.py
   :language: python
   :emphasize-lines: 13,20,23
   :linenos:


Streaming
=========

Gaze data
---------

.. literalinclude:: ../../examples/basic/stream_gaze.py
   :language: python
   :emphasize-lines: 12
   :linenos:

Scene camera video
------------------

.. literalinclude:: ../../examples/basic/stream_scene_camera_video.py
   :language: python
   :emphasize-lines: 23,24
   :linenos:

.. _stream_video_with_overlayed_gaze_example_basic:

Scene camera video with overlayed gaze
--------------------------------------

.. literalinclude:: ../../examples/basic/stream_video_with_overlayed_gaze.py
   :language: python
   :emphasize-lines: 25
   :linenos: