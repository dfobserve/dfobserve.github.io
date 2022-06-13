:py:mod:`dfobserve.checks.check_focusers`
=========================================

.. py:module:: dfobserve.checks.check_focusers


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.checks.check_focusers.AllCheckFocusers



.. py:function:: AllCheckFocusers(movement: int = 1000, tolerance: int = 5, use_birger: bool = True, verbose: bool = False, update: bool = True, **kwargs)

   Check the focusers by moving to a specific value and checking focus
   value is within tolerance, then moving back and checking again.

   :param movement: number of steps to move the focuser
   :type movement: int, default: 1000
   :param tolerance: number of steps a unit can be off by and still marked 'UP'
   :type tolerance: int, default: 5
   :param user_birger: use the birger focusers
   :type user_birger: bool, default: True
   :param verbose: verbose display of test results
   :type verbose: bool, default: True
   :param update: whether to actually mark units down in config file if they fail the test.
   :type update: bool, default: True
   :param \*\*kwargs: any kwargs recognized by SendWebRequestNB


