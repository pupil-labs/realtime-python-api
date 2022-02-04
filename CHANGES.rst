v1.0.0rc4
#########
- Fix examples and documentation
- Finalize first draft of the :ref:`under_the_hood_guide` guide

v1.0.0rc3
#########
- Fix documentation
- Revert: Remove :py:func:`pupil_labs.realtime_api.simple.discover_one_device`
- Revert: Add ``pupil_labs.realtime_api.simple.Network``

v1.0.0rc2
#########
- Apply pre-commit fixes

v1.0.0rc1
#########
- Split :py:mod:`pupil_labs.realtime_api.simple` into multiple files
- Remove ``pupil_labs.realtime_api.discovery.discover_one_device``
- Remove ``pupil_labs.realtime_api.simple.discover_one_device``
- Add ``pupil_labs.realtime_api.simple.Network``
- Add :py:class:`pupil_labs.realtime_api.discovery.Network`

v0.0.12
#######
- Add :py:exc:`pupil_labs.realtime_api.models.UnknownComponentError` and let
  :py:func:`pupil_labs.realtime_api.models.parse_component` raise it when a component
  could not be parsed/mapped
- Drop unknown components in :py:meth:`pupil_labs.realtime_api.models.Status.from_dict`
  and :py:func:`pupil_labs.realtime_api.device.Device.status_updates`, and warn about it

v0.0.11
#######
- Add :py:class:`pupil_labs.realtime_api.models.NetworkDevice`
- Create a new HTTP client session if necessary on :py:class:`pupil_labs.realtime_api.device.Device`'s ``__aenter__`` method

v0.0.10
#######
- Remove ``pupil_labs.realtime_api.simple.Device.recording_recent_action`` and ``pupil_labs.realtime_api.simple.Device.recording_duration_seconds``
- Fix Python 3.7 incompatiblity due to using the ``name`` argument in :py:func:`asyncio.create_task` (added in Python 3.8)

v0.0.9
######
- Fix Python 3.7 compatibility
- Add ``pupil_labs.realtime_api.discovery.discover_one_device``

v0.0.8
######
- Rename ``pupil_labs.realtime_api.basic`` to :py:mod:`pupil_labs.realtime_api.simple`
- Rename ``pupil_labs.realtime_api.basic.Device.read_*()`` methods to ``Device.receive_*()``
- Rename ``pupil_labs.realtime_api.simple.discovered_devices`` to :py:func:`pupil_labs.realtime_api.simple.discover_devices`
- Add :py:func:`pupil_labs.realtime_api.device.Device.status_updates()` generator
- Move status update callback functionality into :py:class:`pupil_labs.realtime_api.device.StatusUpdateNotifier`
- Add :ref:`simple_auto_update_example` example
- Add ``pupil_labs.realtime_api.simple.Device.recording_recent_action`` and ``pupil_labs.realtime_api.simple.Device.recording_duration_seconds``
- Add streaming control functionality to :py:class:`pupil_labs.realtime_api.simple.Device`
    - :py:func:`pupil_labs.realtime_api.simple.Device.streaming_start`
    - :py:func:`pupil_labs.realtime_api.simple.Device.streaming_stop`
    - :py:attr:`pupil_labs.realtime_api.simple.Device.is_currently_streaming`
- Fix examples

v0.0.7
######
- Fix Python 3.7 and 3.8 compatibility

v0.0.6
######
- Add :py:meth:`pupil_labs.realtime_api.simple.Device.receive_matched_scene_video_frame_and_gaze`
- Add simple :ref:`stream_video_with_overlayed_gaze_example_simple` example

v0.0.5
######
- Add guides to documentation
- Add :ref:`stream_video_with_overlayed_gaze_example` example
- Add :py:mod:`pupil_labs.realtime_api.simple` API. See the :ref:`simple_examples`.
- Rename ``pupil_labs.realtime_api.control`` to :py:mod:`pupil_labs.realtime_api.device`.
- Rename ``pupil_labs.realtime_api.base.ControlBase`` to :py:class:`pupil_labs.realtime_api.base.DeviceBase`.
- Rename ``pupil_labs.realtime_api.simple.Control`` to :py:class:`pupil_labs.realtime_api.simple.Device`.
- Rename ``pupil_labs.realtime_api.control.Control`` to :py:class:`pupil_labs.realtime_api.device.Device`.
- Rename ``pupil_labs.realtime_api.models.DiscoveredDevice`` to :py:class:`pupil_labs.realtime_api.models.DiscoveredDeviceInfo`.
- Add sensor property accessors to :py:class:`pupil_labs.realtime_api.simple.Device`.
- Add simple streaming with :py:class:`pupil_labs.realtime_api.simple.Device.receive_scene_video_frame`
  and :py:class:`pupil_labs.realtime_api.simple.Device.receive_gaze_datum`.

v0.0.4
######
- Include examples in documentation
- Implement :py:class:`Recording <pupil_labs.realtime_api.models.Recording>` model class
- Add :py:attr:`Status.recording <pupil_labs.realtime_api.models.Status.recording>` attribute

v0.0.3
######
- Move Control.Error to dedicated :py:exc:`ControlError <pupil_labs.realtime_api.device.DeviceError>` class
- Implement :py:mod:`gaze <pupil_labs.realtime_api.streaming.gaze>` and
    :py:mod:`video <pupil_labs.realtime_api.streaming.video>` streaming

v0.0.2
######
- Require |aiohttp[speedups]|_
- Implement :py:func:`discover_devices <pupil_labs.realtime_api.discovery.discover_devices>`
- Implement :py:class:`Control <pupil_labs.realtime_api.device.Device>`

.. |aiohttp[speedups]| replace:: ``aiohttp[speedups]``
.. _aiohttp[speedups]: https://docs.aiohttp.org/en/stable/
