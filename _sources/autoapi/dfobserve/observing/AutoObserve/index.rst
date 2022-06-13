:py:mod:`dfobserve.observing.AutoObserve`
=========================================

.. py:module:: dfobserve.observing.AutoObserve

.. autoapi-nested-parse::

   Class to handle running a night's observations autonomously.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   dfobserve.observing.AutoObserve.AutoObserve
   dfobserve.observing.AutoObserve.QuickObserve




.. py:class:: AutoObserve(targetlist: list, guide: bool = True, save_log_to: str = None, data_dir_on_pis: str = None)

   Run the observations (i.e., for N iterations, execute the dither commands then expose commands.)

   .. py:method:: mount_pis(self, verbose=True)

      Mount the pis on wsl


   .. py:method:: check_targets_for_issues(self)

      Construct observing plans (if not done) to raise errors if issues arise.


   .. py:method:: pre_observing_checklist(self)


   .. py:method:: set_data_dir(self, save_dir)


   .. py:method:: observe(self, verbose=True, focus_kwargs={})

      Observe! Goes through the observing plan of each target and carries out the required operations and exposures.

      :param verbose: print lots of messages along the way (replicated in log). (Default: True)
      :type verbose: bool (optional)


   .. py:method:: end_of_script_shutdown(self)



.. py:class:: QuickObserve(target: str, ha_tilt: float, oiii_tilt: float, exptime: int, offband_exptime: int, niter: int = 1, save_log_to: str = None, data_dir_on_pis: str = None)

   .. py:method:: setup(self, save_log_to, data_dir_on_pis)


   .. py:method:: mount_pis(self, verbose=True)

      Mount the pis on wsl


   .. py:method:: set_data_dir(self, save_dir)


   .. py:method:: observe(self, dither_east=0, dither_north=0)



