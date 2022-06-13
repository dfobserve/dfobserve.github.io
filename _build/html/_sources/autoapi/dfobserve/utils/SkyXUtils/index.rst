:py:mod:`dfobserve.utils.SkyXUtils`
===================================

.. py:module:: dfobserve.utils.SkyXUtils


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.SkyXUtils.check_target_exists



.. py:function:: check_target_exists(target_name: str, host: str = '127.0.0.1')

   Check whether a target name is recognized by TheSkyX.
   This function constructs a js query which is saved to a temporary
   file that is then sent to TheSkyX via the `skysend` command.

   :param target_name: name to check in the database.
   :type target_name: str
   :param host: IP address associated with TheSkyX server
   :type host: str, default: '127.0.0.1'

   :returns: **found** -- If the target is found, returns true, else false. If another response occurs,
             an error is thrown.
   :rtype: bool


