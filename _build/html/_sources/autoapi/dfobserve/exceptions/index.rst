:py:mod:`dfobserve.exceptions`
==============================

.. py:module:: dfobserve.exceptions


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   exceptions/index.rst


Package Contents
----------------

.. py:exception:: Error

   Bases: :py:obj:`Exception`

   Base class for other exceptions


.. py:exception:: TargetNotFoundError

   Bases: :py:obj:`Error`

   raised when target not in skyx database


.. py:exception:: UnknownError

   Bases: :py:obj:`Error`

   raised when an unknown error has occured


.. py:exception:: UnknownCommunicationError

   Bases: :py:obj:`Error`

   Raised when an unknown error occurs while communicating with a server


.. py:exception:: AstropyNameError

   Bases: :py:obj:`Error`

   raised when a name is not recognized by astropy


.. py:exception:: TargetNotUpError

   Bases: :py:obj:`Error`

   raised when the target is not up at the requested start time


.. py:exception:: EndOfNightError

   Bases: :py:obj:`Error`

   raised when start time calculated is close to the end of the night.


.. py:exception:: FilterNotRecognizedError

   Bases: :py:obj:`Error`

   raised when a filter tilt is entered for a filter name not recognized


.. py:exception:: TargetUptimeError

   Bases: :py:obj:`Error`

   raised when the object uptime is less than requested observing plan time


.. py:exception:: DayTimeError

   Bases: :py:obj:`Error`

   raises when the requested start time is before sunset.


