:py:mod:`dfobserve.utils.MountUtils`
====================================

.. py:module:: dfobserve.utils.MountUtils

.. autoapi-nested-parse::

   Utility functions for controlling the mount.



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.MountUtils.DitherMount
   dfobserve.utils.MountUtils.GuideMount
   dfobserve.utils.MountUtils.HomeMount
   dfobserve.utils.MountUtils.StartMount
   dfobserve.utils.MountUtils.ParkMount
   dfobserve.utils.MountUtils.StopMount
   dfobserve.utils.MountUtils.SlewMount



Attributes
~~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.MountUtils.send_web_request


.. py:data:: send_web_request
   :annotation: = python3 C:/Dragonfly/Programs/SendWebRequestToArray.py

   

.. py:function:: DitherMount(east, north)

   Dither the mount in a certain direction


.. py:function:: GuideMount()

   Attempt to start guiding


.. py:function:: HomeMount()

   Home the Mount


.. py:function:: StartMount()

   Start tracking


.. py:function:: ParkMount()

   Park Mount


.. py:function:: StopMount()

   Stop mount


.. py:function:: SlewMount(target)

   Slew mount to a target

   :param target: target to slew the mount to
   :type target: str


