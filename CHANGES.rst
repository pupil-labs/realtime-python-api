v0.0.3
######
- Move Control.Error to dedicated :py:exc:`ControlError <pupil_labs.realtime_api.control.ControlError>` class
- Implement :py:mod:`gaze <pupil_labs.realtime_api.streaming.gaze>` and
    :py:mod:`video <pupil_labs.realtime_api.streaming.video>` streaming

v0.0.2
######
- Require |aiohttp[speedups]|_
- Implement :py:func:`discover_devices <pupil_labs.realtime_api.discovery.discover_devices>`
- Implement :py:class:`Control <pupil_labs.realtime_api.control.Control>`

.. |aiohttp[speedups]| replace:: ``aiohttp[speedups]``
.. _aiohttp[speedups]: https://docs.aiohttp.org/en/stable/
