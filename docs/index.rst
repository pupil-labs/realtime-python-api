###############################
Pupil Labs' Realtime Python API
###############################

``pupil_labs.realtime_api`` is a Python module to wrapp around
the `Pupil Labs Realtime Network API <https://github.com/pupil-labs/realtime-network-api>`_.

It also offers some convineice functions like gaze<->frame matching and exposes easy-to-use functions and classes to get started without having to know much about advanced programming or network communication!

Use `pip <https://pypi.org/project/pip/>`_ to install the package::

   pip install pupil-labs-realtime-api
   
----
   
## The module comes in two flavours:

1. The ``async`` interface is using Python's asyncio in order to implement non-blocking asynchronous communication.

2. The ``simple`` interface wraps around the ``async`` one sacrificing flexiblity of ease of use. The calls made using the simple mode are blocking. If you don't know what any of this means, that's okay! The simple mode suffices for most use-cases and you usually do not need to understand the differences!

## Getting started

To get started see our code examples :ref:`code_examples`.

We also provide guides as part of the Pupil Invsible and Pupil Cloud documentation: <https://docs.pupil-labs.com/invisible/tutorials/real-time-api/>

## Bugs reports and Contributing

Help us make great tool! Bugs Reports, Suggestions, and Fixes are always welcome.

The source code and issue tracker are both hosted on `GitHub`_.

.. _GitHub: https://github.com/pupil-labs/realtime-python-api

