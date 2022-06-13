:py:mod:`dfobserve.checks`
==========================

.. py:module:: dfobserve.checks


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   check_cameras/index.rst
   check_dragonfly/index.rst
   check_filters/index.rst
   check_focusers/index.rst
   check_mount/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   dfobserve.checks.HardwareStatus
   dfobserve.checks.HardwareStatus
   dfobserve.checks.HardwareStatus



Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.checks.AllCheckFilterTilts
   dfobserve.checks.AllMoveFilters
   dfobserve.checks.AllTiltScienceFilters
   dfobserve.checks.AllGetFilterTilts
   dfobserve.checks.AllCheckFilterTilters
   dfobserve.checks.SendWebRequestNB
   dfobserve.checks.AllCheckCameras
   dfobserve.checks.SendWebRequestNB
   dfobserve.checks.AllCheckFocusers



.. py:class:: HardwareStatus(status_file='/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_CURRENT_STATUS.csv')

   .. py:method:: InitializeHardwareStatus(self)


   .. py:method:: MarkUnitDown(self, unit)


   .. py:method:: MarkUnitUp(self, unit)


   .. py:method:: MarkAccessibleUnitsUp(self)


   .. py:method:: MarkAllUnitsUp(self)


   .. py:method:: MarkAllUnitsDown(self)


   .. py:method:: get_status(self, which='all', verbose=True, return_units=True)



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


.. py:function:: AllGetFilterTilts(which='science', debug=False, **kwargs)

   Gets the tilts for all science filters

   :param which: which filters to return tilts for. Only science ones *should* be needed.
   :type which: str, default: 'science'


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


.. py:function:: SendWebRequestNB(command: str = None, which: str = 'all', skip: list = [], ha_command: str = None, oiii_command: str = None, ha_off_command: str = None, oiii_off_command: str = None, OH_command: str = None, OH_off_command: str = None, all_flathaving_command: str = None, verbose: bool = True, wait_for_response: bool = True, timeout_global: int = 120, timeout_seconds: int = 10, dryrun=False, hardware_config_file=None, **kwargs)

   Send a webrequest to the array but divy up commands by type if requested.
   No required inputs, but if it is run with no inputs, a webrequest will not be sent.

   :param command: command to broadcast to units. This option acts in concert with the `which` keyword argument,
                   which determines where the command will be sent. If further separate commands are needed, use
                   the individually coded keywords. (Default: None)
   :type command: str, optional
   :param which:
                 which units to broadcast the `command` to. Options include
                     `'all'`: send to all lenses. (for example, make all lenses take a 0 second exposure)

                     `'science'`: send to the H-alpha and OIII lenses only. All others will idle.

                     `'science offs'`: send to the offs for H-alpha and OIII only.

                     `'OH'`: send command to the OH on and OH off units
                     `'halpha'`: send to halpha units only
                     `'oiii'`: send to the OIII units only
                 Note that the supplication of any of the more specific keyword args (e.g., `OH_command`) will
                 overwrite the command being sent when this option is used. (Default: 'all')
   :type which: str, optional
   :param skip: any units to skip when sending this command (e.g., those that are down). Should be list of str like 'Dragonfly301'
   :type skip: list, default: []
   :param ha_command: command to send only to the Halpha units. (Default: None)
   :type ha_command: str, optional
   :param oiii_command: command to send only to the OIII units. (Default: None)
   :type oiii_command: str, optional
   :param ha_off_command: command to send only to the offband units of Halpha. (Default: None)
   :type ha_off_command: str, optional
   :param oiii_off_command: command to send only to the offband units of OIII. (Default: None)
   :type oiii_off_command: str, optional
   :param OH_command: command to send only to the OH skyline monitoring units. (Default: None)
   :type OH_command: str, optional
   :param OH_off_command: command to send only to the OH skyline off band units. (Default: None)
   :type OH_off_command: str, optional
   :param all_flathaving_command: command to send to all units with a flip flat attached. (Default: None)
   :type all_flathaving_command: str, optional
   :param verbose: print out info along the way. (Default: True)
   :type verbose: bool, default: True
   :param wait_for_response: wait for all machines to send a response before returning (until timeout). (Default: True)
   :type wait_for_response: bool, default: True
   :param timeout_global: time in seconds to wait while pending machines finish tasks before exiting. (Default: 120)
   :type timeout_global: int, default: 120
   :param timeout_seconds: time in seconds after which to close the connection and mark a machine as failed. (Default: 10)
   :type timeout_seconds: int, default: 10
   :param dryrun: don't execute the command, but show what commands will be sent to which IP addresses. (Default: False)
   :type dryrun: bool, default: False

   :returns: **result_df or WebRequestSummary** -- dataframe (or wrapped version) containing the webrequest results.
   :rtype: pandas.DataFrame


.. py:class:: HardwareStatus(status_file='/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_CURRENT_STATUS.csv')

   .. py:method:: InitializeHardwareStatus(self)


   .. py:method:: MarkUnitDown(self, unit)


   .. py:method:: MarkUnitUp(self, unit)


   .. py:method:: MarkAccessibleUnitsUp(self)


   .. py:method:: MarkAllUnitsUp(self)


   .. py:method:: MarkAllUnitsDown(self)


   .. py:method:: get_status(self, which='all', verbose=True, return_units=True)



.. py:function:: AllCheckCameras(ntests=10, update=True, **kwargs)

   Runs a Camera Check command via the webserver.

   :param ntests: number of tests to run. Each test takes 2 bias images and makes a comparison, and another overarching test uses all frames.
   :type ntests: int, default: 10
   :param update: whether to actually mark units down based on test results
   :type update: bool, default: True
   :param \*\*kwargs: any specific kwargs to pass to SendWebRequestNB


.. py:class:: HardwareStatus(status_file='/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_CURRENT_STATUS.csv')

   .. py:method:: InitializeHardwareStatus(self)


   .. py:method:: MarkUnitDown(self, unit)


   .. py:method:: MarkUnitUp(self, unit)


   .. py:method:: MarkAccessibleUnitsUp(self)


   .. py:method:: MarkAllUnitsUp(self)


   .. py:method:: MarkAllUnitsDown(self)


   .. py:method:: get_status(self, which='all', verbose=True, return_units=True)



.. py:function:: SendWebRequestNB(command: str = None, which: str = 'all', skip: list = [], ha_command: str = None, oiii_command: str = None, ha_off_command: str = None, oiii_off_command: str = None, OH_command: str = None, OH_off_command: str = None, all_flathaving_command: str = None, verbose: bool = True, wait_for_response: bool = True, timeout_global: int = 120, timeout_seconds: int = 10, dryrun=False, hardware_config_file=None, **kwargs)

   Send a webrequest to the array but divy up commands by type if requested.
   No required inputs, but if it is run with no inputs, a webrequest will not be sent.

   :param command: command to broadcast to units. This option acts in concert with the `which` keyword argument,
                   which determines where the command will be sent. If further separate commands are needed, use
                   the individually coded keywords. (Default: None)
   :type command: str, optional
   :param which:
                 which units to broadcast the `command` to. Options include
                     `'all'`: send to all lenses. (for example, make all lenses take a 0 second exposure)

                     `'science'`: send to the H-alpha and OIII lenses only. All others will idle.

                     `'science offs'`: send to the offs for H-alpha and OIII only.

                     `'OH'`: send command to the OH on and OH off units
                     `'halpha'`: send to halpha units only
                     `'oiii'`: send to the OIII units only
                 Note that the supplication of any of the more specific keyword args (e.g., `OH_command`) will
                 overwrite the command being sent when this option is used. (Default: 'all')
   :type which: str, optional
   :param skip: any units to skip when sending this command (e.g., those that are down). Should be list of str like 'Dragonfly301'
   :type skip: list, default: []
   :param ha_command: command to send only to the Halpha units. (Default: None)
   :type ha_command: str, optional
   :param oiii_command: command to send only to the OIII units. (Default: None)
   :type oiii_command: str, optional
   :param ha_off_command: command to send only to the offband units of Halpha. (Default: None)
   :type ha_off_command: str, optional
   :param oiii_off_command: command to send only to the offband units of OIII. (Default: None)
   :type oiii_off_command: str, optional
   :param OH_command: command to send only to the OH skyline monitoring units. (Default: None)
   :type OH_command: str, optional
   :param OH_off_command: command to send only to the OH skyline off band units. (Default: None)
   :type OH_off_command: str, optional
   :param all_flathaving_command: command to send to all units with a flip flat attached. (Default: None)
   :type all_flathaving_command: str, optional
   :param verbose: print out info along the way. (Default: True)
   :type verbose: bool, default: True
   :param wait_for_response: wait for all machines to send a response before returning (until timeout). (Default: True)
   :type wait_for_response: bool, default: True
   :param timeout_global: time in seconds to wait while pending machines finish tasks before exiting. (Default: 120)
   :type timeout_global: int, default: 120
   :param timeout_seconds: time in seconds after which to close the connection and mark a machine as failed. (Default: 10)
   :type timeout_seconds: int, default: 10
   :param dryrun: don't execute the command, but show what commands will be sent to which IP addresses. (Default: False)
   :type dryrun: bool, default: False

   :returns: **result_df or WebRequestSummary** -- dataframe (or wrapped version) containing the webrequest results.
   :rtype: pandas.DataFrame


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


