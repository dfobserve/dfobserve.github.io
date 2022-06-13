:py:mod:`dfobserve.utils.FilterTilterUtils`
===========================================

.. py:module:: dfobserve.utils.FilterTilterUtils

.. autoapi-nested-parse::

   Utility functions for interacting with the filter tilters via the webserver



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.FilterTilterUtils.AllTiltScienceFilters
   dfobserve.utils.FilterTilterUtils.AllMoveFilters
   dfobserve.utils.FilterTilterUtils.TiltFiltersByType
   dfobserve.utils.FilterTilterUtils.AllGetFilterTilts
   dfobserve.utils.FilterTilterUtils.AllCheckFilterTilts
   dfobserve.utils.FilterTilterUtils.AllSetTiltsToZero



.. py:function:: AllTiltScienceFilters(ha_tilt: float, oiii_tilt: float, debug: bool = False, **kwargs)

   Tilt all filters of a given filter type to a specific value.

   :param ha_tilt: amount to tilt Ha filters. Must be between -20 and 20
   :type ha_tilt: float
   :param oiii_tilt: angle to tilt OIII filters. Must be between -20 and 20
   :type oiii_tilt: float
   :param debug: debug flag for testing (executes a dryrun).
   :type debug: bool, default: False
   :param \*\*kwargs: kwargs recognized by SendWebRequestNB
   :type \*\*kwargs: optional


.. py:function:: AllMoveFilters(ha_move: float, oiii_move: float, debug: bool = False, **kwargs)

   Tilt all filters of a given filter type by a specific value.

   :param ha_move: amount to tilt Ha filters. Must be between -20 and 20
   :type ha_move: float
   :param oiii_move: angle to tilt OIII filters. Must be between -20 and 20
   :type oiii_move: float
   :param debug: debug flag for testing (executes a dryrun).
   :type debug: bool, default: False
   :param \*\*kwargs: kwargs recognized by SendWebRequestNB
   :type \*\*kwargs: optional


.. py:function:: TiltFiltersByType(filt_name, tilt_angle)


.. py:function:: AllGetFilterTilts(which='science', debug=False, **kwargs)

   Gets the tilts for all science filters

   :param which: which filters to return tilts for. Only science ones *should* be needed.
   :type which: str, default: 'science'


.. py:function:: AllCheckFilterTilts(ha_tilt: float, oiii_tilt: float, tol: float = 0.3, verbose=False, **kwargs)

   Query the filter tilters and obtain the current tilt. Check that tilts are within specified tolerance.

   :param ha_tilt: expected tilt for Halpha
   :type ha_tilt: float
   :param oiii_tilt: expected tilt for [OIII]
   :type oiii_tilt: float
   :param tol: tolerance between true and expected tilt to return an all OK.
   :type tol: float, default: 0.3

   :returns: * **res** (*bool*) -- True if all filters in tolerance, False if not
             * **bad** (*list*) -- List of any filters that returned bad tilts


.. py:function:: AllSetTiltsToZero()


