v0.0.8
######
- Rename ``pupil_labs.realtime_api.basic`` to :py:mod:`pupil_labs.realtime_api.simple`
- Rename ``pupil_labs.realtime_api.basic.Device.read_*()`` methods to ``Device.receive_*()``
- Rename ``pupil_labs.realtime_api.simple.discovered_devices`` to :py:func:`pupil_labs.realtime_api.simple.discover_devices`
- Add :py:func:`pupil_labs.realtime_api.device.Device.status_updates()` generator
- Move status update callback functionality into :py:class:`pupil_labs.realtime_api.device.StatusUpdateNotifier`
- Add :ref:`simple_auto_update_example` example

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
