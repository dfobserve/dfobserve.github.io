:py:mod:`dfobserve.checks.check_filters`
========================================

.. py:module:: dfobserve.checks.check_filters

.. autoapi-nested-parse::

   Module for testing that filters are healthy and behaving normally.
   Check executes several tilt commands and confirms that the filters return angles that are within tolerance.



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.checks.check_filters.AllCheckFilterTilters



.. py:function:: AllCheckFilterTilters(tol: float = 0.3, update: bool = True, check_angles: list = [5, 0], verbose: bool = True, plot: bool = False, save_plot: bool = False, save_plot_name: str = 'FilterTilterChecks.png')

   Confirm that Tilters are not stuck and are moving well.

   :param tol: tolerance desired between actual tilt and input tilt.
   :type tol: float, defaut: 0.3
   :param update: whether to actually mark units down in the config file based on test results.
   :type update: bool, default: True
   :param check_angles: angles to move to and confirm unit tilts are within tolerance.
   :type check_angles: list, default: [5,0]
   :param verbose: Full outputs when running the check.
   :type verbose: bool, default: True
   :param plot: plot up the results of the difference between tilt goal and tilts for all units at each check angle
   :type plot: bool, default: False
   :param save_plot: whether to save a plot to disk
   :type save_plot: bool, default: False
   :param save_plot_name: path/name to save file to disk.
   :type save_plot_name: str, default: 'FilterTilterChecks.png'


