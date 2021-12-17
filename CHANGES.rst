v0.0.3
######
- Move Control.Error to dedicated :py:exc:`ControlError <pupil_labs.realtime_api.control.ControlError>` class
- Implement :py:mod:`Control <pupil_labs.realtime_api.streaming>`

v0.0.2
######
- Require |aiohttp[speedups]|_
- Implement :py:func:`discover_devices <pupil_labs.realtime_api.discovery.discover_devices>`
- Implement :py:class:`Control <pupil_labs.realtime_api.control.Control>`

.. |aiohttp[speedups]| replace:: ``aiohttp[speedups]``
.. _aiohttp[speedups]: https://docs.aiohttp.org/en/stable/
