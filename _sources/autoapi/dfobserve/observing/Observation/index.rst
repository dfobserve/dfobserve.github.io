:py:mod:`dfobserve.observing.Observation`
=========================================

.. py:module:: dfobserve.observing.Observation

.. autoapi-nested-parse::

   Create detailed Observation parameters for individual targets including their calibration frames.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   dfobserve.observing.Observation.Observation



Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.observing.Observation.get_sunset
   dfobserve.observing.Observation.get_sunrise
   dfobserve.observing.Observation.get_morning_twilight
   dfobserve.observing.Observation.get_moonset
   dfobserve.observing.Observation.get_moonrise



.. py:class:: Observation(target: str, exptime: int = 3600, iterations: int = 2, do_focus: bool = True, min_altitude: float = 35.0)

   .. py:method:: check_target(self)

      Confirm that the input target is recognized by TheSkyX and astropy, else raise an error


   .. py:method:: calc_target_rise(self, date='today', utcoffset=-6, return_local=True)

      Calculate the time when the target rises above the set minimum altitude (after sunset) For now, always 'today'.
      If the target rises before sunset, sunset time is returned.

      :param date: date to use in YYYY-MM-DD or 'today'.
      :type date: str, default: 'today'
      :param utcoffset: utc offset between NMS and UTC
      :type utcoffset: float, default: -6
      :param return_local: whether to return the time in local time. Otherwise, UTC is returned
      :type return_local: bool, default: True

      :returns: **target_set** -- astropy Time object containing the time (either in UTC or local.)
      :rtype: astropy.time.Time


   .. py:method:: calc_target_set(self, date='today', utcoffset=-6, return_local=True)

      Calculate the time when the target sets below the set minimum altitude (after sunset) For now, always 'today'.

      :param date: date to use in YYYY-MM-DD or 'today'.
      :type date: str, default: 'today'
      :param utcoffset: utc offset between NMS and UTC
      :type utcoffset: float, default: -6
      :param return_local: whether to return the time in local time. Otherwise, UTC is returned
      :type return_local: bool, default: True

      :returns: **target_set** -- astropy Time object containing the time (either in UTC or local.)
      :rtype: astropy.time.Time


   .. py:method:: calc_target_altitude(self, utcoffset=-6)

      Calculate the target's current altitude.


   .. py:method:: set_tilts(self, filtname, angle)

      Set the filter angles for either Halpha or OIII.

      :param filtname: Either 'Halpha' or 'OIII' ('halpha','oiii', '[OIII]', and 'o3' accepted)
      :type filtname: str
      :param angle: tilt angle. Must be between -20 and 20.
      :type angle: float


   .. py:method:: configure_observation(self, wait_until: str = None, off_band_exptime: int = 600, off_band_throughout: bool = True, dither_angle: int = 25, dither_pattern: list = [5, 6, 3, 2, 1, 4, 7, 8, 9], randomize_dithers: bool = False)

      Set up when and how observations should occur

      :param wait_until:
                         key to not start observations until a certain time. If none supplied, start immediately. Options include
                             `None`: observations will start immediately upon script being run.
                             `'sunset'` : observations will wait until sunset local time

                             `'moonset'` : observations will wait until the moon sets

                             `'target_rise'` : observations will wait until object rises above min_alt.
                             `'HH:MM:SS'`: observations will start at the requested time. Default is local, but adding UTC to the end of the string will use UTC.
      :type wait_until: str, optional
      :param off_band_exptime: exptime (seconds) for the continuum/OH filters. These shorter
                               exposures can be taken once, or throughout the longer on exposure.
                               (Default : 600)
      :type off_band_exptime: int, default : 600
      :param off_band_throughout: keep taking off-band images throughout on band exp? (Default : True)
      :type off_band_throughout: bool, default : True
      :param dither_angle: angle to use (in arcmin) for dithers off the target. (Default : 25)
      :type dither_angle: int, default : 25
      :param dither_pattern: The pattern on which to dither. A 3x3 grid is used for pointings, with each grid
                             point separated by `dither_angle`. The grid is

                                     1    2       3

                                     4    5       6

                                     7    8       9

                             By default, the pattern starts on the object (pos 5) moves to 6, and wraps
                             counter-clockwise around. You can specify any dither sequence of any length.

                             By setting to a subset of the numbers 1-9, if `iterations` is greater than
                             the sequence length, a new sequence will start back at the first defined position.
                             For example, if iterations = 4, and `dither_pattern` is set to [4,6], then the observing
                             sequence will be position 4,6, 4,6.
      :type dither_pattern: list, optional
      :param randomize_dithers: take the dither position list and randomize it. (Default : False)
      :type randomize_dithers: bool, default : False


   .. py:method:: configure_calibrations(self, n_darks: int = 0, dark_exptime: int = 10, take_darks: str = 'after', n_flats: int = 0, flat_exptime: int = 10, take_flats: str = 'after')

      n_darks : int, default: 0
          number of dark frames to take. (Default : 0)
      dark_exptime : int, default: 10
          exposure time in seconds. (Default : 10)
      take_darks : str, default: after
          when to take darks. Options include
              `'before'` : before obs of target

              `'between'` : between iterations

              `'after'` : after obs of target

              `'all'` : before, after, and between iterations
      n_flats : int, optional
          number of flats to take at end of observation. (Default : 0)
      flat_exptime : int, default: 10
          exptime for flats (Default : 10)
      take_flats : str, optional
          when to take flats. Options include
              'before' : before obs of target
              'between' : between iterations
              'after' : after obs of target
              'all' : before, after, and between iterations


   .. py:method:: configure_standards(self, use: str = 'nearest', when: str = 'after', n_standards: int = 0, exptime: int = 60)

      Configure the capturing of standard star images for calibration.

      :param use:
                  which standard star(s) to use. Options include
                      `'nearest'` : use the standard in the list nearest to the target on-sky

                      `'<name>'` : a specific star name as present in the starlist.
                  (Default : 'nearest')
      :type use: str, default: 'nearest'
      :param when:
                   when to take standard star exposures. Options include
                       `'before'` : before observations of the target

                       `'between'` : between iterations on the target

                       `'after'` : after the target has been observed

                       `'all'` : before, between, and after iterations.
      :type when: str, default: 'after'
      :param n_standards: how many iterations to take on the standard star. (Default : 0)
      :type n_standards: int, default: 0
      :param exptime: exposure time (in seconds) for the standard star observations. (Default : 60)
      :type exptime: int, default: 60


   .. py:method:: construct_observing_plan(self, date='today')

      Based on all selected options, determine how observations of this
      target should be carried out.

      :param date: date for which to construct plan. Format YYYY-MM-DD or 'today'.
      :type date: str, default: 'today'

      :returns: **obs_plan** -- A simple list containing mini dictionaries with observing params (ultimately the same info as the dataframe below).
      :rtype: list


   .. py:method:: check_observing_timings(self, date)

      Checks to ensure the requested observation start times do not conflict with logic.


   .. py:method:: view_observing_plan(self, sysout: bool = True, write_to_log: bool = False, logfile=None)

      Takes an observing plan list and prints it nicely

      :param sysout: whether to print the observing plan to stdout
      :type sysout: bool, default: True
      :param write_to_log: whether to write to a logfile (generally for during observations)
      :type write_to_log: bool, default: False
      :param logfile: if write_to_log is True, the logfile to write to must be given here.
      :type logfile: str, default: None


   .. py:method:: test_observing_plan(self)

      Run a series of tests on the proposed observing plan



.. py:function:: get_sunset(date='today', utcoffset=-6, return_local=True)

   Retrieve the time of sunset at NMS on a certain date.

   :param date: date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
   :type date: str, default: 'today'
   :param utcoffset: offset between UTC and NMS. Usually -6 but might change during daylights savings
   :type utcoffset: int, default: -6
   :param return_local: return the time in local time. If False, time is returned in UTC
   :type return_local: bool, default: True

   :returns: **sunset_time** -- time of sunset in either UTC or local as requested
   :rtype: astropy.time.Time


.. py:function:: get_sunrise(date='today', utcoffset=-6, return_local=True)

   Retrieve the time of sunrise at NMS on a certain date.

   :param date: date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
   :type date: str, default: 'today'
   :param utcoffset: offset between UTC and NMS. Usually -6 but might change during daylights savings
   :type utcoffset: int, default: -6
   :param return_local: return the time in local time. If False, time is returned in UTC
   :type return_local: bool, default: True

   :returns: **sunset_time** -- time of sunset in either UTC or local as requested
   :rtype: astropy.time.Time


.. py:function:: get_morning_twilight(date='today', utcoffset=-6, return_local=True)

   Retrieve the time of morning 18 degree twilight at NMS on a certain date.

   :param date: date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
   :type date: str, default: 'today'
   :param utcoffset: offset between UTC and NMS. Usually -6 but might change during daylights savings
   :type utcoffset: int, default: -6
   :param return_local: return the time in local time. If False, time is returned in UTC
   :type return_local: bool, default: True

   :returns: **sunset_time** -- time of sunset in either UTC or local as requested
   :rtype: astropy.time.Time


.. py:function:: get_moonset(date='today', utcoffset=-6, set_altitude=10, return_local=True)

   Retrieve the time of moonset at NMS on a certain date. More formally, the time
   the moon drops below a certain altitude *after* sunset on that date.

   :param date: date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
   :type date: str, default: 'today'
   :param utcoffset: offset between UTC and NMS. Usually -6 but might change during daylights savings
   :type utcoffset: int, default: -6
   :param set_altitude: altitude in degrees at which to consider the moon 'set'.
   :type set_altitude: float, default: 10
   :param return_local: return the time in local time. If False, time is returned in UTC
   :type return_local: bool, default: True

   :returns: **moonset_time** -- time of moonset in either UTC or local as requested
   :rtype: astropy.time.Time


.. py:function:: get_moonrise(date='today', utcoffset=-6, rise_altitude=10, return_local=True)

   Retrieve the time of moonrise at NMS on a certain date. More formally, the time
   the moon rises above a certain altitude *after* sunset on that date.

   :param date: date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
   :type date: str, default: 'today'
   :param utcoffset: offset between UTC and NMS. Usually -6 but might change during daylights savings
   :type utcoffset: int, default: -6
   :param rise_altitude: altitude in degrees at which to consider the moon 'set'.
   :type rise_altitude: float, default: 10
   :param return_local: return the time in local time. If False, time is returned in UTC
   :type return_local: bool, default: True

   :returns: **moonrise_time** -- time of moonrise in either UTC or local as requested
   :rtype: astropy.time.Time


