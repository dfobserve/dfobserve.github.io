:py:mod:`dfobserve.checks.check_cameras`
========================================

.. py:module:: dfobserve.checks.check_cameras


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.checks.check_cameras.AllCheckCameras



.. py:function:: AllCheckCameras(ntests=10, update=True, **kwargs)

   Runs a Camera Check command via the webserver.

   :param ntests: number of tests to run. Each test takes 2 bias images and makes a comparison, and another overarching test uses all frames.
   :type ntests: int, default: 10
   :param update: whether to actually mark units down based on test results
   :type update: bool, default: True
   :param \*\*kwargs: any specific kwargs to pass to SendWebRequestNB


