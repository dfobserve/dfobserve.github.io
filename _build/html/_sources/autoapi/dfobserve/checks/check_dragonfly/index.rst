:py:mod:`dfobserve.checks.check_dragonfly`
==========================================

.. py:module:: dfobserve.checks.check_dragonfly


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.checks.check_dragonfly.AllCheckDragonfly



.. py:function:: AllCheckDragonfly(skip: list = [], update: bool = True, camera_kwargs: dict = {}, filtertilter_kwargs: dict = {}, focuser_kwargs: dict = {})

   Check the health of the DFNB system and mark pis down if needed.

   :param skip: List of tests to skip along the way. Options include 'mount','network','focusers','filters','cameras'
   :type skip: list, default: []
   :param update: Whether to update the config file with the results of each test (i.e., actually mark the pis down).
   :type update: bool, default: True
   :param camera_kwargs: keyword arguments accepted by AllCheckCameras to modify the nature of the tests run.
   :type camera_kwargs: dict, default: {}
   :param filtertilter_kwargs: keyword arguments accepted by AllCheckFilterTiters to modify the nature of the tests run.
   :type filtertilter_kwargs: dict, default: {}
   :param focuser_kwargs: keyword arguments accepted by AllCheckFocusers to modify the nature of the tests run.
   :type focuser_kwargs: dict, default: {}


