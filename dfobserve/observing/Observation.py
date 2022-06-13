"""
Create detailed Observation parameters for individual targets including their calibration frames.
"""

import numpy as np
import pandas as pd
import os, sys
import subprocess as sp
import astropy.units as u

from dfobserve.exceptions.exceptions import (
    AstropyNameError,
    DayTimeError,
    EndOfNightError,
    FilterNotRecognizedError,
    TargetNotUpError,
    TargetUptimeError,
)
from ..logging import Logger
from astropy.coordinates import SkyCoord, get_sun, get_moon, EarthLocation, AltAz
from astropy.wcs import WCS
from astropy.time import Time
from datetime import datetime, timedelta, date as dt_date
from ..utils import SkyXUtils

send_web_request = "python3 C :/Dragonfly/Programs/SendWebRequestToArray.py"

__all__ = [
    "Observation",
    "get_sunset",
    "get_moonset",
    "get_moonrise",
    "get_sunrise",
    "get_morning_twilight",
]


class Observation:
    def __init__(
        self,
        target: str,  # Target recognized by TheSkyX
        exptime: int = 3600,  # seconds
        iterations: int = 2,  # number of exposures to obtain
        do_focus: bool = True,  # do a focus run before starting
        min_altitude: float = 35.0,  # degrees
    ):
        """
        Initialize an Observation object. An observation is defined by its `target`
        and the settings for how it should be observed.

        Parameters
        ----------
        target : str
            name of target to observe. Must be recognized by TheSkyX
        exptime : int, default : 3600
            exposure time in seconds. (Default : 3600)
        iterations : int, default : 2
            number of exposures to obtain. (Default : 2)
        do_focus : bool, default : True
            whether to do a focus run before the iteration. (Default : True)
        min_altitude : float, default : 35
            Minimum altitude to use. If a target is below this altitude at the beginning of an exposure, the
            script will bail and the telescope will slew to a safe position.
        """

        self.target = target
        self.exptime = exptime
        self.do_focus = do_focus
        self.iterations = iterations
        self.min_altitude = min_altitude

    def check_target(self):
        """
        Confirm that the input target is recognized by TheSkyX and astropy, else raise an error
        """
        # Check astropy
        try:
            c = SkyCoord.from_name(self.target)
        except:
            raise AstropyNameError("SkyCoord.from_name(target) raised an exception.")
        # Check TheSkyX
        SkyXUtils.check_target_exists(self.target)
        return

    def calc_target_rise(self, date="today", utcoffset=-6, return_local=True):
        """
        Calculate the time when the target rises above the set minimum altitude (after sunset) For now, always 'today'.
        If the target rises before sunset, sunset time is returned.

        Parameters
        ----------
        date: str, default: 'today'
            date to use in YYYY-MM-DD or 'today'.
        utcoffset: float, default: -6
            utc offset between NMS and UTC
        return_local: bool, default: True
            whether to return the time in local time. Otherwise, UTC is returned

        Returns
        -------
        target_set: astropy.time.Time
            astropy Time object containing the time (either in UTC or local.)
        """
        obsloc = EarthLocation(
            lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
        )
        now = datetime.now()
        if date == "today":
            dt_string = now.strftime("%Y-%m-%d")
        else:
            dt_string = date
        midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
        delta_midnight = np.linspace(-12, 12, 500) * u.hr
        obs_times = midnight + delta_midnight
        frame = AltAz(obstime=obs_times, location=obsloc)
        target_alt = SkyCoord.from_name(self.target).transform_to(frame).alt
        sunset = get_sunset(return_local=False, date=date)
        target_rise_ind = np.where(
            (target_alt > self.min_altitude * u.deg) & (obs_times > sunset)
        )[0][0]

        target_rise = obs_times[target_rise_ind]
        if return_local:
            return target_rise + utcoffset * u.hr
        else:
            return target_rise

    def calc_target_set(self, date="today", utcoffset=-6, return_local=True):
        """
        Calculate the time when the target sets below the set minimum altitude (after sunset) For now, always 'today'.

        Parameters
        ----------
        date: str, default: 'today'
            date to use in YYYY-MM-DD or 'today'.
        utcoffset: float, default: -6
            utc offset between NMS and UTC
        return_local: bool, default: True
            whether to return the time in local time. Otherwise, UTC is returned

        Returns
        -------
        target_set: astropy.time.Time
            astropy Time object containing the time (either in UTC or local.)
        """
        obsloc = EarthLocation(
            lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
        )
        now = datetime.now()
        if date == "today":
            dt_string = now.strftime("%Y-%m-%d")
        else:
            dt_string = date
        midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
        delta_midnight = np.linspace(-12, 12, 500) * u.hr
        obs_times = midnight + delta_midnight
        frame = AltAz(obstime=obs_times, location=obsloc)
        target_alt = SkyCoord.from_name(self.target).transform_to(frame).alt
        target_set_ind = np.where(
            (target_alt < self.min_altitude * u.deg)
            & (obs_times > self.calc_target_rise(return_local=False, date=date))
        )[0][0]

        target_set = obs_times[target_set_ind]
        if return_local:
            return target_set + utcoffset * u.hr
        else:
            return target_set

    def calc_target_altitude(self, utcoffset=-6):
        """
        Calculate the target's current altitude.
        """
        obsloc = EarthLocation(
            lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
        )
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        time_check = Time(dt_string) - utcoffset * u.hr
        frame = AltAz(obstime=time_check, location=obsloc)
        target_alt = SkyCoord.from_name(self.target).transform_to(frame).alt
        if target_alt < self.min_altitude:
            return False
        else:
            return True

    def set_tilts(self, filtname, angle):
        """
        Set the filter angles for either Halpha or OIII.

        Parameters
        ----------
        filtname : str
            Either 'Halpha' or 'OIII' ('halpha','oiii', '[OIII]', and 'o3' accepted)
        angle : float
            tilt angle. Must be between -20 and 20.
        """
        if np.abs(angle) >= 20:
            raise ValueError("Must choose an angle between -20 and 20")
        if filtname in ["Halpha", "halpha", "HALPHA"]:
            self.ha_tilt = angle
        elif filtname in ["OIII", "oiii", "o3", "[OIII]"]:
            self.oiii_tilt = angle
        else:
            raise FilterNotRecognizedError("filter name not in allowed list")

    def configure_observation(
        self,
        wait_until: str = None,
        off_band_exptime: int = 600,  # seconds
        off_band_throughout: bool = True,
        dither_angle: int = 25,  # arcmin
        dither_pattern: list = [5, 6, 3, 2, 1, 4, 7, 8, 9],
        randomize_dithers: bool = False,
    ):
        """
        Set up when and how observations should occur

        Parameters
        ----------
        wait_until : str, optional
            key to not start observations until a certain time. If none supplied, start immediately. Options include
                `None`: observations will start immediately upon script being run.
                `'sunset'` : observations will wait until sunset local time \n
                `'moonset'` : observations will wait until the moon sets \n
                `'target_rise'` : observations will wait until object rises above min_alt.
                `'HH:MM:SS'`: observations will start at the requested time. Default is local, but adding UTC to the end of the string will use UTC.
        off_band_exptime : int, default : 600
            exptime (seconds) for the continuum/OH filters. These shorter
            exposures can be taken once, or throughout the longer on exposure.
            (Default : 600)
        off_band_throughout : bool, default : True
            keep taking off-band images throughout on band exp? (Default : True)
        dither_angle : int, default : 25
            angle to use (in arcmin) for dithers off the target. (Default : 25)
        dither_pattern : list, optional
            The pattern on which to dither. A 3x3 grid is used for pointings, with each grid
            point separated by `dither_angle`. The grid is

                    1 \t 2 \t 3 \n
                    4 \t 5 \t 6 \n
                    7 \t 8 \t 9

            By default, the pattern starts on the object (pos 5) moves to 6, and wraps
            counter-clockwise around. You can specify any dither sequence of any length.

            By setting to a subset of the numbers 1-9, if `iterations` is greater than
            the sequence length, a new sequence will start back at the first defined position.
            For example, if iterations = 4, and `dither_pattern` is set to [4,6], then the observing
            sequence will be position 4,6, 4,6.
        randomize_dithers : bool, default : False
            take the dither position list and randomize it. (Default : False)
        """
        # if wait_until is not None:
        #     if wait_until not in ["sunset", "moonset", "target_rise"]:
        #         try:
        #             in_date = (
        #                 datetime.now().strftime("%Y-%m-%d") + " " + self.wait_until
        #             )
        #             time = Time(in_date)
        #             self.wait_until = wait_until
        #         except:
        #             raise AssertionError("input time must by HH:MM:SS format")
        #     else:
        #         self.wait_until = wait_until
        # else:
        #     self.wait_until = None
        self.wait_until = wait_until
        # Check altitudes at wait until times.
        self.off_band_exptime = off_band_exptime
        self.off_band_throughout = off_band_throughout
        if off_band_throughout:
            self.n_cals = int(np.floor(self.exptime / self.off_band_exptime))
        else:
            self.n_cals = 1
        self.dither_angle = dither_angle
        self.dither_pattern = dither_pattern
        if randomize_dithers:
            np.random.shuffle(self.dither_pattern)
        self.dither_dict = {
            0: [self.dither_angle, self.dither_angle],  # pos east and north
            1: [0, self.dither_angle],
            2: [-self.dither_angle, self.dither_angle],
            3: [self.dither_angle, 0],
            4: [0, 0],
            5: [-self.dither_angle, 0],
            6: [self.dither_angle, -self.dither_angle],
            7: [0, -self.dither_angle],
            8: [-self.dither_angle, -self.dither_angle],
        }

    def configure_calibrations(
        self,
        n_darks: int = 0,
        dark_exptime: int = 10,
        take_darks: str = "after",
        n_flats: int = 0,
        flat_exptime: int = 10,
        take_flats: str = "after",
    ):
        """
        n_darks : int, default: 0
            number of dark frames to take. (Default : 0)
        dark_exptime : int, default: 10
            exposure time in seconds. (Default : 10)
        take_darks : str, default: after
            when to take darks. Options include
                `'before'` : before obs of target \n
                `'between'` : between iterations \n
                `'after'` : after obs of target \n
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
        """
        self.calibration_dict = {
            "n_darks": n_darks,
            "dark_exptime": dark_exptime,
            "n_flats": n_flats,
            "flat_exptime": flat_exptime,
            "take_darks": take_darks,
            "take_flats": take_flats,
        }

    def configure_standards(
        self,
        use: str = "nearest",  # use nearest standard star
        when: str = "after",  # when to take standards
        n_standards: int = 0,  # number of exposures
        exptime: int = 60,  # exptime in seconds
    ):
        """
        Configure the capturing of standard star images for calibration.

        Parameters
        ----------
        use : str, default: 'nearest'
            which standard star(s) to use. Options include
                `'nearest'` : use the standard in the list nearest to the target on-sky\n
                `'<name>'` : a specific star name as present in the starlist.
            (Default : 'nearest')
        when : str, default: 'after'
            when to take standard star exposures. Options include
                `'before'` : before observations of the target \n
                `'between'` : between iterations on the target \n
                `'after'` : after the target has been observed \n
                `'all'` : before, between, and after iterations.
        n_standards : int, default: 0
            how many iterations to take on the standard star. (Default : 0)
        exptime : int, default: 60
            exposure time (in seconds) for the standard star observations. (Default : 60)
        """
        self.standards_dict = {
            "use": use,
            "when": when,
            "n_standards": n_standards,
            "exptime": exptime,
        }

    def construct_observing_plan(self, date="today"):
        """
        Based on all selected options, determine how observations of this
        target should be carried out.

        Parameters
        ----------
        date: str, default: 'today'
            date for which to construct plan. Format YYYY-MM-DD or 'today'.

        Returns
        -------
        obs_plan: list
            A simple list containing mini dictionaries with observing params (ultimately the same info as the dataframe below).
        """
        # Setup default configurations if not done by user
        if not hasattr(self, "calibration_dict"):
            self.configure_calibrations()
        if not hasattr(self, "standards_dict"):
            self.configure_standards()
        if not hasattr(self, "wait_until"):
            self.configure_observation()

        # Check timing of target rises and sets, etc.
        self.check_observing_timings(date)
        # establish stuff that should happen before, between, and after obs
        # Check for needed flats first (they need flips so)
        obs_plan = []
        if self.calibration_dict["take_flats"] in ["before", "all"]:
            nflats = self.calibration_dict["n_flats"]
            if nflats > 0:
                exptime = self.calibration_dict["flat_exptime"]
                for i in range(nflats):
                    obs_plan.append({"type": "flat", "exptime": exptime})
        # Check if darks should be taken before
        if self.calibration_dict["take_darks"] in ["before", "all"]:
            ndarks = self.calibration_dict["n_darks"]
            if ndarks > 0:
                exptime = self.calibration_dict["dark_exptime"]
                for i in range(ndarks):
                    obs_plan.append({"type": "dark", "exptime": exptime})
        # Check if a focus run is called for
        if self.do_focus:
            obs_plan.append({"type": "focus"})

        # Check if standard star should be taken before
        if self.standards_dict["when"] in ["before", "all"]:
            if self.standards_dict["n_standards"] > 0:
                exptime = self.standards_dict["exptime"]
                n_standards = self.standards_dict["n_standards"]
                use = self.standards_dict["use"]
                for i in range(n_standards):
                    obs_plan.append(
                        {"type": "standard", "exptime": exptime, "use": use}
                    )

        # Now move on to the target observations
        for i in range(self.iterations):
            obs_plan.append(
                {"type": "science", "target": self.target, "exptime": self.exptime}
            )
            obs_plan.append(
                {
                    "type": "calibration",
                    "target": self.target,
                    "exptime": self.off_band_exptime,
                    "n": self.n_cals,
                }
            )
            # Check for cals between
            if i < (self.iterations - 1):
                if self.calibration_dict["take_flats"] in ["between", "all"]:
                    nflats = self.calibration_dict["n_flats"]
                    if nflats > 0:
                        exptime = self.calibration_dict["flat_exptime"]
                        for i in range(nflats):
                            obs_plan.append({"type": "flat", "exptime": exptime})
                # Check if darks should be taken between
                if self.calibration_dict["take_darks"] in ["between", "all"]:
                    ndarks = self.calibration_dict["n_darks"]
                    if ndarks > 0:
                        exptime = self.calibration_dict["dark_exptime"]
                        for i in range(ndarks):
                            obs_plan.append({"type": "dark", "exptime": exptime})
                # Check if standard star should be taken between
                if self.standards_dict["when"] in ["between", "all"]:
                    if self.standards_dict["n_standards"] > 0:
                        exptime = self.standards_dict["exptime"]
                        n_standards = self.standards_dict["n_standards"]
                        use = self.standards_dict["use"]
                        for i in range(n_standards):
                            obs_plan.append(
                                {"type": "standard", "exptime": exptime, "use": use}
                            )

        # Check what to do after observing target
        # Check if flats should be taken after
        # Check if standard star should be taken after
        if self.standards_dict["when"] in ["after", "all"]:
            if self.standards_dict["n_standards"] > 0:
                exptime = self.standards_dict["exptime"]
                n_standards = self.standards_dict["n_standards"]
                use = self.standards_dict["use"]
                for i in range(n_standards):
                    obs_plan.append(
                        {"type": "standard", "exptime": exptime, "use": use}
                    )
        if self.calibration_dict["take_flats"] in ["after", "all"]:
            nflats = self.calibration_dict["n_flats"]
            if nflats > 0:
                exptime = self.calibration_dict["flat_exptime"]
                for i in range(nflats):
                    obs_plan.append({"type": "flat", "exptime": exptime})
        # Check if darks should be taken after
        if self.calibration_dict["take_darks"] in ["after", "all"]:
            ndarks = self.calibration_dict["n_darks"]
            if ndarks > 0:
                exptime = self.calibration_dict["dark_exptime"]
                for i in range(ndarks):
                    obs_plan.append({"type": "dark", "exptime": exptime})
        self.observing_plan = pd.DataFrame(obs_plan)
        self.observing_plan["n"] = [
            1 if np.isnan(i) else i for i in self.observing_plan.n
        ]
        # Calculate total exposure time on target
        total_exptime = 0
        for n, i in enumerate(obs_plan):
            if i["type"] in ["standard", "science", "flat", "dark"]:
                total_exptime += int(i["exptime"])
        self.total_exptime_hours = total_exptime / 3600.0
        if self.total_exptime_hours > self.target_uptime:
            raise TargetUptimeError(
                f"Minimum exposure time on {self.target} ({self.total_exptime_hours:.2f} hrs) is longer than its up-time ({self.target_uptime:.2f} hrs)."
            )

        self.obs_plan = obs_plan
        return obs_plan

    def check_observing_timings(self, date):
        """
        Checks to ensure the requested observation start times do not conflict with logic.
        """
        # Establish when to start observations.
        if self.wait_until == "sunset":
            sunset = get_sunset(date=date)
            target_rise = self.calc_target_rise(date=date)
            if sunset < target_rise:
                raise TargetNotUpError(
                    f"You selected a sunset start for {self.target}, but {self.target} \n is not above minimum altitude ({self.min_altitude} deg) at sunset. \n You probably want None or target_rise"
                )
            else:
                self.OBS_START = sunset
        elif self.wait_until == "moonset":
            self.OBS_START = get_moonset(date=date)
            if date == "today":
                day = (datetime.now() + timedelta(days=1)).day
                time_compare = Time(
                    f"{datetime.now().strftime('%Y-%m')}-{day} 04:00:00"
                )
            else:
                y = int(date.split("-")[0])
                m = int(date.split("-")[1])
                d = int(date.split("-")[2])
                dt = dt_date(y, m, d) + timedelta(days=1)
                time_compare = Time(f"{dt.year}-{dt.month}-{dt.day} 04:00:00")
            if self.OBS_START > time_compare:
                raise EndOfNightError(
                    f"Selected Start Time for {self.target} as moonset but moonset is after 4 am local."
                )
        elif self.wait_until == None:
            self.wait_until = "None (Now/after previous)"
            self.OBS_START = "N/A"
        elif self.wait_until == "target_rise":
            self.OBS_START = self.calc_target_rise(date=date)
            if date == "today":
                day = (datetime.now() + timedelta(days=1)).day
                time_compare = Time(
                    f"{datetime.now().strftime('%Y-%m')}-{day} 04:00:00"
                )
            else:
                y = int(date.split("-")[0])
                m = int(date.split("-")[1])
                d = int(date.split("-")[2])
                dt = dt_date(y, m, d) + timedelta(days=1)
                time_compare = Time(f"{dt.year}-{dt.month}-{dt.day} 04:00:00")
            if self.OBS_START > time_compare:
                raise EndOfNightError(
                    f"{self.target} appears to rise above minimum altitude ({self.min_altitude} deg) after 4 am local..."
                )
        else:
            # assume exact time is given
            start_hour = int(self.wait_until.split(":")[0])
            if date == "today":
                if start_hour < 12:
                    day = (datetime.now() + timedelta(days=1)).day
                    in_date = (
                        datetime.now().strftime(f"%Y-%m-{day}") + " " + self.wait_until
                    )
                else:
                    in_date = (
                        datetime.now().strftime("%Y-%m-%d") + " " + self.wait_until
                    )
            else:
                if start_hour < 12:
                    y = int(date.split("-")[0])
                    m = int(date.split("-")[1])
                    d = int(date.split("-")[2])
                    dt = dt_date(y, m, d) + timedelta(days=1)
                    in_date = f"{dt.year}-{dt.month}-{dt.day}" + " " + self.wait_until
                else:
                    in_date = date + " " + self.wait_until
            self.OBS_START = Time(in_date)
            sunset = get_sunset(date=date)
            sunrise = get_sunrise(date=date)
            moonset = get_moonset(date=date)
            if self.OBS_START < sunset:
                raise DayTimeError("Start time is before sunset.")
            elif self.OBS_START > sunrise:
                raise DayTimeError("Start time is after sunrise.")
            elif self.OBS_START < moonset:
                print("WARNING: START TIME is before moon sets. (allowing...)")

        self.target_uptime = self.calc_target_set(date=date) - self.calc_target_rise(
            date=date
        )
        self.target_uptime = self.target_uptime.to_datetime().seconds / 3600

    def view_observing_plan(
        self, sysout: bool = True, write_to_log: bool = False, logfile=None
    ):
        """
        Takes an observing plan list and prints it nicely

        Parameters
        ----------
        sysout: bool, default: True
            whether to print the observing plan to stdout
        write_to_log: bool, default: False
            whether to write to a logfile (generally for during observations)
        logfile: str, default: None
            if write_to_log is True, the logfile to write to must be given here.
        """
        if not hasattr(self, "observing_plan"):
            observing_plan = self.construct_observing_plan()
        else:
            observing_plan = self.obs_plan
        total_exptime = 0
        total_exps = 0
        out = f"""
=================== OBSERVING PLAN FOR {self.target} ===================
Summary of user-selected configurations for this observing run. Here
are the frames that will be captured....
====================================================================
Observing was set to start at {self.wait_until}, which today is at 

{self.OBS_START} local time. 

For Reference, sunset is at {get_sunset()} local time today and
               moonset is at {get_moonset()} local time today.

Science Exposures will be taken in the following dither pattern :
{self.dither_pattern} 
on a 

    1   2   3

    4   5   6

    7   8   9

grid. Because the number of science iterations is {self.iterations},
positions {self.dither_pattern[0 :self.iterations]} will be observed.

The dither angle between pointings is {self.dither_angle} arcminutes.
"""
        if hasattr(self, "ha_tilt"):
            out += f"""
The input tilt angles are
    H-alpha : {self.ha_tilt}
    [OIII] : {self.oiii_tilt}
            """
        out += f"""


====================================================================
Framelist of proposed observations
====================================================================

"""
        for n, i in enumerate(observing_plan):
            if i["type"] == "standard":
                add = f"""{n}. {i['type']} frame with exptime : {i['exptime']} s using {i['use']} standard star
"""
                out += add
                total_exptime += int(i["exptime"])
                total_exps += 1
            elif i["type"] == "calibration":
                add = f"""{n}. Co-expose of {i['n']} {i['type']} FRAME(s) with EXPTIME : {i['exptime']} s
"""
                out += add
                # total_exptime += int(i['exptime'])
                total_exps += int(i["n"])
            elif i["type"] == "focus":
                add = f"""-------------------------------------
{n}. Focus Run 
-------------------------------------
"""
                out += add
            else:
                add = f"""{n}. {i['type']} frame with exptime : {i['exptime']} s 
"""
                out += add
                total_exptime += int(i["exptime"])
                total_exps += 1
        hours = total_exptime / 3600
        out += f"""\n
========================================================================
Total Exposure Time (on sky) : {total_exptime} seconds ({hours :.2f} hours)
Total Number of (non focus) Exposures : {total_exps}
[does not include focus runs]
========================================================================
"""
        if write_to_log:
            with open(logfile, "a") as f:
                f.write(out)
        if sysout:
            print(out)
        return

    def test_observing_plan(self):
        """
        Run a series of tests on the proposed observing plan
        """
        # check if target is up at proposed start time

        # check if target will set before end of iterations

        pass


def get_sunset(date="today", utcoffset=-6, return_local=True):
    """
    Retrieve the time of sunset at NMS on a certain date.

    Parameters
    ----------
    date: str, default: 'today'
        date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
    utcoffset: int, default: -6
        offset between UTC and NMS. Usually -6 but might change during daylights savings
    return_local: bool, default: True
        return the time in local time. If False, time is returned in UTC

    Returns
    -------
    sunset_time: astropy.time.Time
        time of sunset in either UTC or local as requested
    """
    obsloc = EarthLocation(
        lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
    )
    if date == "today":
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
    else:
        dt_string = date
    midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
    delta_midnight = np.linspace(-12, 12, 500) * u.hr
    obs_times = midnight + delta_midnight
    frame = AltAz(obstime=obs_times, location=obsloc)
    sun = get_sun(obs_times).transform_to(frame)
    sunset_ind = np.where(sun.alt < 0 * u.deg)[0][0]
    if return_local:
        sunset_time = obs_times[sunset_ind] + utcoffset * u.hr
        return sunset_time
    else:
        sunset_utc = obs_times[sunset_ind]
        return sunset_utc


def get_sunrise(date="today", utcoffset=-6, return_local=True):
    """
    Retrieve the time of sunrise at NMS on a certain date.

    Parameters
    ----------
    date: str, default: 'today'
        date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
    utcoffset: int, default: -6
        offset between UTC and NMS. Usually -6 but might change during daylights savings
    return_local: bool, default: True
        return the time in local time. If False, time is returned in UTC

    Returns
    -------
    sunset_time: astropy.time.Time
        time of sunset in either UTC or local as requested
    """
    obsloc = EarthLocation(
        lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
    )
    if date == "today":
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
    else:
        dt_string = date
    midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
    delta_midnight = np.linspace(-12, 12, 500) * u.hr
    obs_times = midnight + delta_midnight
    frame = AltAz(obstime=obs_times, location=obsloc)
    sun = get_sun(obs_times).transform_to(frame)
    sunrise_ind = np.where(sun.alt < 0 * u.deg)[0][-1]
    if return_local:
        sunrise_time = obs_times[sunrise_ind] + utcoffset * u.hr
        return sunrise_time
    else:
        sunrise_utc = obs_times[sunrise_ind]
        return sunrise_utc


def get_morning_twilight(date="today", utcoffset=-6, return_local=True):
    """
    Retrieve the time of morning 18 degree twilight at NMS on a certain date.

    Parameters
    ----------
    date: str, default: 'today'
        date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
    utcoffset: int, default: -6
        offset between UTC and NMS. Usually -6 but might change during daylights savings
    return_local: bool, default: True
        return the time in local time. If False, time is returned in UTC

    Returns
    -------
    sunset_time: astropy.time.Time
        time of sunset in either UTC or local as requested
    """
    obsloc = EarthLocation(
        lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
    )
    if date == "today":
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
    else:
        dt_string = date
    midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
    delta_midnight = np.linspace(-12, 12, 500) * u.hr
    obs_times = midnight + delta_midnight
    frame = AltAz(obstime=obs_times, location=obsloc)
    sun = get_sun(obs_times).transform_to(frame)
    twilight_ind = np.where(sun.alt < -18.0 * u.deg)[0][-1]
    if return_local:
        twilight_time = obs_times[twilight_ind] + utcoffset * u.hr
        return twilight_time
    else:
        twilight_utc = obs_times[twilight_ind]
        return twilight_utc


def get_moonset(date="today", utcoffset=-6, set_altitude=10, return_local=True):
    """
    Retrieve the time of moonset at NMS on a certain date. More formally, the time
    the moon drops below a certain altitude *after* sunset on that date.

    Parameters
    ----------
    date: str, default: 'today'
        date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
    utcoffset: int, default: -6
        offset between UTC and NMS. Usually -6 but might change during daylights savings
    set_altitude: float, default: 10
        altitude in degrees at which to consider the moon 'set'.
    return_local: bool, default: True
        return the time in local time. If False, time is returned in UTC

    Returns
    -------
    moonset_time: astropy.time.Time
        time of moonset in either UTC or local as requested
    """
    obsloc = EarthLocation(
        lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
    )
    if date == "today":
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
    else:
        dt_string = date
    midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
    delta_midnight = np.linspace(-12, 18, 500) * u.hr
    obs_times = midnight + delta_midnight
    frame = AltAz(obstime=obs_times, location=obsloc)
    sunset = get_sunset(date=date)
    moon = get_moon(obs_times).transform_to(frame)
    moon_ind = np.where((moon.alt > set_altitude * u.deg) & (obs_times > sunset))[0][-1]
    if return_local:
        moonset_time = obs_times[moon_ind] + utcoffset * u.hr
        return moonset_time
    else:
        moonset_utc = obs_times[moon_ind]
        return moonset_utc


def get_moonrise(date="today", utcoffset=-6, rise_altitude=10, return_local=True):
    """
    Retrieve the time of moonrise at NMS on a certain date. More formally, the time
    the moon rises above a certain altitude *after* sunset on that date.

    Parameters
    ----------
    date: str, default: 'today'
        date for which to retrieve sunset. If not 'today', a string of the format YYYY-MM-DD.
    utcoffset: int, default: -6
        offset between UTC and NMS. Usually -6 but might change during daylights savings
    rise_altitude: float, default: 10
        altitude in degrees at which to consider the moon 'set'.
    return_local: bool, default: True
        return the time in local time. If False, time is returned in UTC

    Returns
    -------
    moonrise_time: astropy.time.Time
        time of moonrise in either UTC or local as requested
    """
    obsloc = EarthLocation(
        lon=-105.5302 * u.deg, lat=32.9024 * u.deg, height=2225 * u.m
    )
    if date == "today":
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
    else:
        dt_string = date
    midnight = Time(f"{dt_string} 23:59:59") - utcoffset * u.hr
    delta_midnight = np.linspace(-12, 18, 500) * u.hr
    obs_times = midnight + delta_midnight
    frame = AltAz(obstime=obs_times, location=obsloc)
    sunset = get_sunset(date=date)
    moon = get_moon(obs_times).transform_to(frame)
    moon_ind = np.where((moon.alt > rise_altitude * u.deg) & (obs_times > sunset))[0][0]
    if return_local:
        moonrise_time = obs_times[moon_ind] + utcoffset * u.hr
        return moonrise_time
    else:
        moonrise_utc = obs_times[moon_ind]
        return moonrise_utc
