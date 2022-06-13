:py:mod:`dfobserve.utils.CameraUtils`
=====================================

.. py:module:: dfobserve.utils.CameraUtils

.. autoapi-nested-parse::

   Utility functions for interacting with the cameras.



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.CameraUtils.AllScienceExposure
   dfobserve.utils.CameraUtils.AllExpose
   dfobserve.utils.CameraUtils.AllFlatFieldExposure
   dfobserve.utils.CameraUtils.AllDarkExposure
   dfobserve.utils.CameraUtils.AutoFocus
   dfobserve.utils.CameraUtils.AllSetCameraTemperatures
   dfobserve.utils.CameraUtils.AllCheckCameraTemperatures



.. py:function:: AllScienceExposure(exptime: int, off_exptime: int, n_offs: int, oh_exptime: int = None, extras: dict = None, wait_readout: int = 60, debug: bool = False, **kwargs)

   Execute a standard science exposure


.. py:function:: AllExpose(exptime: int, which: str = 'all', extras: dict = None, wait_readout: int = 60, **kwargs)

   Very Simply, take an exposure on a certain set of cameras.

   :param exptime: exposure time in seconds
   :type exptime: int
   :param which:
                 which cameras to send to. Options include
                     `'all'`: send to all lenses. (for example, make all lenses take a 0 second exposure)

                     `'science'`: send to the H-alpha and OIII lenses only. All others will idle.

                     `'science offs'`: send to the offs for H-alpha and OIII only.

                     `'OH'`: send command to the OH on and OH off units
                     `'halpha'`: send to halpha units only
                     `'oiii'`: send to the OIII units only
                 (Default: 'all')
   :type which: str (optional)
   :param wait_readout: how long to wait in seconds for the exposure to read out before disconnecting.
   :type wait_readout: int (optional)


.. py:function:: AllFlatFieldExposure(exptime: int, n: int = 1, which: str = 'science', extras=None, wait_readout: int = 60, **kwargs)

   Take a flatfield using all the science filters. (or some other set)


.. py:function:: AllDarkExposure(exptime: int, which: str = 'all', extras=None, wait_readout: int = 60, **kwargs)

   Take a dark exposure.


.. py:function:: AutoFocus(exptime: int = 3, focus_lower: float = 1000, focus_upper: float = 1000, nsteps: int = 25, use_sextractor: bool = True, use_birger: bool = True, non_adaptive: bool = True, fit: bool = True, extras=None, **kwargs)


.. py:function:: AllSetCameraTemperatures(temperature: float, which: str = 'all', **kwargs)


.. py:function:: AllCheckCameraTemperatures(temperature: float, which: str = 'all', tol: float = 5, verbose: bool = True, **kwargs)


