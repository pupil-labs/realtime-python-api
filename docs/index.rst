###############################
Pupil Labs' Realtime Python API
###############################

``pupil_labs.realtime_api`` is a Python module to wrap around
the `Pupil Labs Realtime Network API <https://github.com/pupil-labs/realtime-network-api>`_.

It also offers some convenience functions like gaze↔frame matching and exposes
easy-to-use functions and classes to get started without having to know much about
advanced programming or network communication!

Use `pip <https://pypi.org/project/pip/>`_ to install the package::

   pip install pupil-labs-realtime-api

Getting Started
---------------

The module comes in two flavours, we recommend using the `simple` version.

1. The ``async`` interface is using Python's `asyncio`_ in order to implement
   non-blocking asynchronous communication.

2. The ``simple`` interface wraps around the ``async`` one sacrificing flexibility for
   the sake of ease of use. The calls made using the simple mode are blocking. If you
   don't know what any of this means, that's okay! The simple mode suffices for most
   use-cases and you usually do not need to understand the differences!

To get started with either version, see our code examples :ref:`code_examples`.

We also provide more detailed guides as part of the Pupil Invisible and Pupil Cloud
documentation: `docs.pupil-labs.com`_

Bug Reports and Contributing
----------------------------

Help us make great tool! Bugs reports, suggestions, and fixes are always welcome.


The source code and issue tracker are both hosted on `GitHub`_.

.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _docs.pupil-labs.com: https://docs.pupil-labs.com/invisible/how-tos/integrate-with-the-real-time-api/introduction/
.. _GitHub: https://github.com/pupil-labs/realtime-python-api


Table of Contents
-----------------

.. toctree::
   :maxdepth: 3

   examples/index
   guides/index
   api/index
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
