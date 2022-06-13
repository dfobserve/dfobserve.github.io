"""
Class to handle running a night's observations autonomously.
"""
import numpy as np
import pandas as pd
import subprocess as sp
import time
from dfobserve.exceptions.exceptions import EndOfNightError
from dfobserve.utils.SkyXUtils import StartAutoGuide, StopAutoGuide
from dfobserve.webserver.WebRequests import SendWebRequestNB
from ..logging import Logger
from datetime import datetime
import os
from astropy.time import Time

import astropy.units as u
from ..utils.MountUtils import SlewMount, StartMount
from ..utils.NMS_utils import isRoofOpen
from ..utils.FilterTilterUtils import (
    AllTiltScienceFilters,
    AllGetFilterTilts,
    AllCheckFilterTilts,
)
from ..utils.MountUtils import DitherMount, GuideMount, StopMount, ParkMount
from ..utils.FlipFlatUtils import (
    AllCloseFlipFlats,
    AllOpenFlipFlats,
    AllTurnOffFlipFlaps,
    AllTurnOnFlipFlaps,
)
from dfobserve.utils.CameraUtils import (
    AllDarkExposure,
    AllExpose,
    AllScienceExposure,
    AllFlatFieldExposure,
    AllSetCameraTemperatures,
    AutoFocus,
    AllCheckCameraTemperatures,
)

from dfobserve.utils.HardwareUtils import HardwareStatus

from ..observing import get_morning_twilight

__all__ = ["AutoObserve", "QuickObserve"]


class AutoObserve:
    """
    Run the observations (i.e., for N iterations, execute the dither commands then expose commands.)
    """

    def __init__(
        self,
        targetlist: list,
        guide: bool = True,
        save_log_to: str = None,
        data_dir_on_pis: str = None,
    ):

        self.targetlist = targetlist
        self.guide = guide
        self.log = Logger()
        if save_log_to is None:
            self.save_dir = "./"
        else:
            self.save_dir = save_log_to
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
        logfile = self.save_dir + f"{dt_string}_ObservingLog.log"
        print(f"Global Logfile for this run will be saved to {logfile}")
        self.log.set_file(logfile)
        self.log.info("Mounting the pis")
        self.mount_pis()
        self.set_data_dir(data_dir_on_pis)

    def mount_pis(self, verbose=True):
        """
        Mount the pis on wsl
        """
        res = sp.run(
            "python3 C:/Dragonfly/Programs/MountPisOnPC.py",
            shell=True,
            capture_output=True,
        )
        if verbose:
            print(res)

    def check_targets_for_issues(self):
        """
        Construct observing plans (if not done) to raise errors if issues arise.
        """
        for target in self.targetlist:
            if not hasattr(target, "observing_plan"):
                target.construct_observing_plan()
                # This should throw errors if there are issues
        return

    def pre_observing_checklist(self):
        if not isRoofOpen():
            return False
        else:
            return True

    def set_data_dir(self, save_dir):
        send_web_request = "python3 C:/Dragonfly/Programs/SendWebRequestToArray.py"
        if save_dir is None:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d")
            print(f"Setting path to /data/{dt_string} on each pi")
            self.log.info(f"Setting path to /data/{dt_string} on each pi")
            command = f"{send_web_request} 'mkdir -p /data/{dt_string}'"
            res = sp.run(command, shell=True, capture_output=True)
            check = f"{send_web_request} 'ls -ltr  /data | tail -n 1'"
            res = sp.run(check, shell=True, capture_output=True)
            print(res)
            self.data_path = f"/data/{dt_string}/"
            # self.log.info(res)

        else:
            print(f"Setting path to /data/{save_dir} on each pi")
            command = f"{send_web_request} 'mkdir -p /data/{save_dir}'"
            res = sp.run(command, shell=True, capture_output=True)
            check = f"{send_web_request} 'ls -ltr  /data | tail -n 1'"
            res = sp.run(check, shell=True, capture_output=True)
            print(res)
            # self.log.info(res)
            self.data_path = f"/data/{save_dir}/"

    def observe(self, verbose=True, focus_kwargs={}):
        """
        Observe! Goes through the observing plan of each target and carries out the required operations and exposures.

        Parameters
        ----------
        verbose: bool (optional)
            print lots of messages along the way (replicated in log). (Default: True)
        """
        self.hardware_status = HardwareStatus()
        # Last check of targets
        self.check_targets_for_issues()
        # Establish start time:
        obs_start_time = self.targetlist[0].OBS_START
        if obs_start_time == "N/A":
            # then start now
            pass
        else:
            current_time = datetime.now()
            time_till_start = obs_start_time - current_time
            time_till_start = time_till_start.total_seconds()
            time_till_start_hours = (time_till_start * u.s).to(u.hr)
            if time_till_start < 0:
                if verbose:
                    print(
                        "We are currently after the requested start time! Starting obs now."
                    )
                    self.log.info(
                        "We are currently after the requested start time! Starting obs now."
                    )
                pass
            else:
                self.log.info(
                    f"Currently {time_till_start_hours:.2f} hrs till requested start. Sleeping {time_till_start:.2f} seconds."
                )
                if verbose:
                    print(
                        f"Currently {time_till_start_hours:.2f} hrs till requested start. Sleeping {time_till_start:.2f} seconds."
                    )
                time.sleep(time_till_start)

        if verbose:
            print("Running Pre-observing checklist before starting")
        self.log.info("Running Pre-observing checklist before starting")
        start_obs = False
        while not start_obs:
            # if it's morning twilight, give up
            current_time = Time(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            morning_twilight = get_morning_twilight()  # local time.
            if current_time > morning_twilight:
                self.log.info("It is morning! Exiting the Script Now.")
                raise EndOfNightError("End of night reached, observing never started.")
            check = self.pre_observing_checklist()
            if check:
                start_obs = True
                if verbose:
                    print("Pre Observing Checklist passed. Starting observations")
                self.log.info("Pre Observing Checklist passed. Starting observations")
            else:
                self.log.info(
                    "Pre Observing Checklist failed. Trying again in 60 seconds"
                )
                if verbose:
                    print("Pre Observing Checklist failed. Trying again in 60 seconds")
                time.sleep(60)

        # We're good to go. Let's cool the cameras.
        # Loading up Bad things to skip.
        skip = self.hardware_status.get_status(
            which="down", verbose=False, return_units=True
        )

        self.log.vspace()
        self.log.section()
        self.log.info("Setting Cameras to -20 deg and sleeping 120 s.")
        r = AllSetCameraTemperatures(-20, skip=skip)
        time.sleep(120)
        continue_on = False
        temp_counter = 0
        while not continue_on:
            self.log.info("Checking Camera Temperatures")
            r, b = AllCheckCameraTemperatures(-20)
            bad_units = list(r.loc[r.isGood == False, "Name"].values)
            if b == 0:
                continue_on = True
            elif temp_counter > 3:
                print(f"{b} Cameras not in tolerence but 3 tries exceeded.")
                self.log.warning(
                    f"{b} Cameras not in tolerence but 3 tries exceeded. \n Setting bad cameras to DOWN"
                )
                for bad_camera in bad_units:
                    self.hardware_status.MarkUnitDown(bad_camera)
            else:
                temp_counter += 1
                print(
                    f"{b} Cameras not in tolerence. Sending command again and sleeping 120s."
                )
                self.log.warning(
                    f"{b} Cameras not in tolerence. Sending command again and sleeping 120s."
                )
                r = AllSetCameraTemperatures(-20)
                time.sleep(120)

        self.log.info("Camera Temperatures Set")

        self.log.section()

        for target in self.targetlist:
            self.log.info(
                f"============== Starting Run for Target {target} =============="
            )
            # Check target altitude and refuse to slew if it is at a stupid altitude.
            if not target.check_target_altitude():
                if verbose:
                    print("WARNING: Target below minimum elevation. Skipping Target.")
                self.log.warning("Target below minimum elevation. Skipping Target.")
                continue  # go to next target
            else:
                if verbose:
                    print("Target above minimum altitude. Beginning Target run.")
                self.log.info("Target above minimum altitude. Beginning Target run.")

            current_time = Time(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if current_time > morning_twilight:
                if verbose:
                    print(
                        "It is morning. We will not observe this target. Starting Shutdown."
                    )
                    self.log.warning(
                        "It is morning. We will not observe this target. Starting shutdown."
                    )
                    self.end_of_script_shutdown()
                    raise EndOfNightError("Script Exited due to it being morning.")

            # Slew to Target
            self.log.info(f"Slewing to {target.target}")
            res = SlewMount(target.target)
            self.log.info(res.stdout.decode("utf-8"))
            # Currently the perl script. Should wait till its done.
            # Start tracking
            if verbose:
                print("Starting Mount Tracking")
            self.log.info("Starting Mount Tracking")
            res = StartMount()
            self.log.info(res.stdout.decode("utf-8"))

            if verbose:
                print(
                    f"Executing Tilt Commands of ha: {target.ha_tilt}, oiii: {target.oiii_tilt}"
                )
            self.log.info(
                f"Executing Tilt Commands of ha: {target.ha_tilt}, oiii: {target.oiii_tilt}"
            )
            # Tilt to Target Tilts
            skip = self.hardware_status.get_status(
                which="down", verbose=False, return_units=True
            )
            res = AllTiltScienceFilters(
                ha_tilt=target.ha_tilt, oiii_tilt=target.oiii_tilt, skip=skip
            )
            self.log.info("Command sent, sleeping 10 to let settle.")
            if verbose:
                print("Command sent, sleeping 10 to let settle.")
            time.sleep(10)
            continue_on = False
            try_tilt = 0
            while not continue_on:
                self.log.info("Checking that Tilts are within tolerance")
                if verbose:
                    print("Checking that Tilts are within tolerance")
                ha_df, oiii_df = AllCheckFilterTilts(
                    target.ha_tilt, target.oiii_tilt, skip=skip
                )
                nbad_ha = len(ha_df.loc[ha_df.isGood == False])
                nbad_oiii = len(oiii_df.loc[oiii_df.isGood == False])
                all_bad = nbad_ha + nbad_oiii
                if all_bad == 0:
                    self.log.info("All Filters within tolerance of TiltGoal.")
                    if verbose:
                        print("All Filters within tolerance of TiltGoal.")
                    continue_on = True
                elif try_tilt > 3:
                    self.log.warning(
                        f"{all_bad} Filters out of tolerance but number of tries (3) reached. These will be marked DOWN."
                    )
                    if verbose:
                        print(
                            f"WARNING::: {all_bad} Filters out of tolerance but number of tries (3) reached. These will be marked DOWN."
                        )
                    for bad_ha in list(ha_df.loc[ha_df.isGood == False, "Name"].values):
                        self.hardware_status.MarkUnitDown(bad_ha)
                    for bad_oiii in list(
                        oiii_df.loc[oiii_df.isGood == False, "Name"].values
                    ):
                        self.hardware_status.MarkUnitDown(bad_oiii)
                    continue_on = True
                else:
                    try_tilt += 1
                    if verbose:
                        print(
                            f"Warning: {all_bad} Filters are out of tolerence. Trying again."
                        )
                        print(ha_df)
                        print(oiii_df)
                    self.log.warning(
                        f"{all_bad} Filters are out of tolerence. Trying again."
                    )
                    res = AllTiltScienceFilters(
                        ha_tilt=target.ha_tilt, oiii_tilt=target.oiii_tilt, skip=skip
                    )
                    time.sleep(10)

            dither_index = 0
            for row in target.observing_plan.index:
                current_time = Time(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                if current_time > morning_twilight:
                    if verbose:
                        print(
                            "It is morning. We will not observe this target. Starting Shutdown."
                        )
                        self.log.warning(
                            "It is morning. We will not observe this target. Starting shutdown."
                        )
                        self.end_of_script_shutdown()
                        raise EndOfNightError("Script Exited due to it being morning.")
                # Assuming we are good to take a frame
                if not target.check_target_altitude():
                    if verbose:
                        print(
                            "WARNING: Target below minimum elevation. Skipping Target."
                        )
                    self.log.warning("Target below minimum elevation. Skipping Target.")
                    continue

                skip = self.hardware_status.get_status(
                    which="down", verbose=False, return_units=True
                )
                current = target.observing_plan.loc[row, "type"]
                if current == "flat":
                    # Close Flipflats
                    if verbose:
                        print("Closing Flipflats for flats")
                    self.log.info("Closing Flipflats for flats")
                    res = AllCloseFlipFlats()
                    # self.log.info(res.to_string())
                    if verbose:
                        print("Turning on the flip flats")
                    self.log.info("Turning on FlipFlaps")
                    res = AllTurnOnFlipFlaps()
                    # self.log.info(res.to_string())
                    # Take N Flats
                    nexp = target.observing_plan.loc[row, "n"]
                    for i in range(nexp):
                        if verbose:
                            print(f"Exposing Flat {i} / {nexp}")
                        self.log.info(f"Exposing Flat {i} / {nexp}")
                        response = AllFlatFieldExposure(
                            target.observing_plan.loc[row, "exptime"], skip=skip
                        )
                        # self.log.info(response.to_string())
                    if verbose:
                        print("Finished Flats, Opening Flip Flats")
                    self.log.info("Finished Flats, turning off and opening Flip Flats")
                    # Open Flipflats
                    res = AllTurnOffFlipFlaps()
                    # self.log.info(res.to_string())
                    res = AllOpenFlipFlats()
                    # self.log.info(res.to_string())
                elif current == "standard":
                    if target.observing_plan.loc[row, "use"] == "nearest":
                        # find the nearest standard star and go take N exposures there.
                        pass
                elif current == "focus":
                    # carry out a focus run
                    res = AutoFocus(**focus_kwargs, skip=skip)

                elif current == "dark":
                    # take a dark frame (all cameras).
                    res = AllDarkExposure(
                        skip=skip
                    )  # assumes all cameras, we could set which='science'
                    self.log.info(res.to_string())
                elif current == "science":
                    # Execute a dither from the main pointing
                    dither = target.dither_dict[dither_index]
                    dither_index += 1
                    res = DitherMount(dither[0], dither[1])  # is a preformatted string
                    self.log.info(res)

                    # Start Guiding
                    if verbose:
                        print("Starting AutoGuider and sleeping 15 sec")
                    self.log.info("Activating Autoguider and sleeping 15 sec.")
                    r = StartAutoGuide()
                    time.sleep(15)
                    self.log.info(r.stdout.decode("utf-8"))
                    # Assume the next row in the table has the info for cals to take
                    if target.observing_plan.loc[row + 1, "type"] == "calibration":
                        if verbose:
                            print("Starting Science Exposure.")
                        self.log.info("STARTING SCIENCE EXPOSURE")
                        res = AllScienceExposure(
                            exptime=target.observing_plan.loc[row, "exptime"],
                            off_exptime=target.observing_plan.loc[row + 1, "exptime"],
                            n_offs=target.observing_plan.loc[row + 1, "n"],
                            name=target.target,
                            skip=skip,
                        )
                        # self.info.log(res.to_string())

                    else:
                        self.log.warning(
                            "Row after science in obs plan was NOT calibration... it should be!"
                        )
                        self.log.info("As a result, we wont take any offs")
                        self.log.info("STARTING SCIENCE EXPOSURE")
                        if verbose:
                            print("STARTING SCIENCE EXPOSURE")
                        res = AllExpose(
                            exptime=target.observing_plan.loc[row, "exptime"],
                            which="science",
                            skip=skip,
                        )
                        # self.info.log(res.to_string())
                    if verbose:
                        print("Stopping Autoguider.")
                    # Stop Autoguiding after exposure
                    self.log.info("Stopping Autoguider.")
                    r = StopAutoGuide()
                    self.log.info(r.stdout.decode("utf-8"))
                    # Dither Back to center before handling what comes next
                    if verbose:
                        print("Dithering back to original pointing before continuing.")
                    self.log.info(
                        "Dithering back to original pointing before continuing."
                    )
                    res = SlewMount(target.target)
                    self.log.info(res.to_string())

        self.end_of_script_shutdown()

        return

    def end_of_script_shutdown(self):
        # End of night shutdown stuff
        self.log.info("Setting Camera Temperatures to 30 and sleeping 30 s.")
        r = AllSetCameraTemperatures(30)
        self.log.info(r.to_string)
        time.sleep(30)

        self.log.info("Closing Flip Flats")
        r = AllCloseFlipFlats()
        # self.log.info(r.to_string())

        self.log.info("Parking and Stopping Mount.")
        r = ParkMount()
        self.log.info(r.to_string())
        r = StopMount()
        self.log.info(r.to_string())

        self.log.info("Observations Complete.")
        return


class QuickObserve:
    def __init__(
        self,
        target: str,
        ha_tilt: float,
        oiii_tilt: float,
        exptime: int,
        offband_exptime: int,
        niter: int = 1,
        save_log_to: str = None,
        data_dir_on_pis: str = None,
    ):
        """
        Quickly Observe a target. Science Exposures Only.
        This version carries out NO checks against your stupidity.
        Make sure the dome is open.
        Make sure it's night time.
        Make Sure you've cooled the cameras.
        Make sure you have enough time to carry out the obs you have asked for.

        The number of offband exposures will be exptime // offband_exptime

        Parameters
        ----------
        target: str
            target name. MUST be recognized by the SkyX and astropy.
        ha_tilt: float
            tilt for ha filter (-20,20).
        oiii_tilt: float
            tilt for oiii filter (-20,20).
        exptime: int
            length of science exposure (and OH exposures) in seconds
        offband_exptime: int
            length of offband exposures in seconds
        niter: int
            number of science frames to take
        save_log_to: str, default: None
            where to save the logfile. Default None means current directory.
        data_dir_on_pis: str, default: None
            where to save raw files on pis. Default is
        """
        self.target = target
        self.ha_tilt = ha_tilt
        self.oiii_tilt = oiii_tilt
        self.exptime = exptime
        self.offband_exptime = offband_exptime
        self.niter = niter
        self.n_offs = int(np.floor(self.exptime / self.offband_exptime))
        self.setup(save_log_to=save_log_to, data_dir_on_pis=data_dir_on_pis)
        self.mount_pis()
        self.hardware_status = HardwareStatus()

    def setup(self, save_log_to, data_dir_on_pis):
        self.log = Logger()
        if save_log_to is None:
            self.save_dir = "./"
        else:
            self.save_dir = save_log_to
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
        logfile = self.save_dir + f"{dt_string}_ObservingLog_QUICK.log"
        print(f"Global Logfile for this run will be saved to {logfile}")
        self.log.set_file(logfile)
        self.log.info("Mounting the pis")
        self.mount_pis()
        self.set_data_dir(data_dir_on_pis)

    def mount_pis(self, verbose=True):
        """
        Mount the pis on wsl
        """
        res = sp.run(
            "python3 C:/Dragonfly/Programs/MountPisOnPC.py",
            shell=True,
            capture_output=True,
        )
        if verbose:
            print(res)

    def set_data_dir(self, save_dir):
        send_web_request = "python3 C:/Dragonfly/Programs/SendWebRequestToArray.py"
        if save_dir is None:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d")
            print(f"Setting path to /data/{dt_string} on each pi")
            self.log.info(f"Setting path to /data/{dt_string} on each pi")
            command = f"{send_web_request} 'mkdir -p /data/{dt_string}'"
            res = sp.run(command, shell=True, capture_output=True)
            check = f"{send_web_request} 'ls -ltr  /data | tail -n 1'"
            res = sp.run(check, shell=True, capture_output=True)
            print(res)
            self.log.info(res)
            return f"/data/{dt_string}"
        else:
            print(f"Setting path to /data/{save_dir} on each pi")
            command = f"{send_web_request} 'mkdir -p /data/{save_dir}'"
            res = sp.run(command, shell=True, capture_output=True)
            check = f"{send_web_request} 'ls -ltr  /data | tail -n 1'"
            res = sp.run(check, shell=True, capture_output=True)
            print(res)
            self.log.info(res)
            return

    def observe(self, dither_east=0, dither_north=0):
        self.log.info(f"Slewing to {self.target}")
        res = SlewMount(self.target)
        self.log.info(res.stdout.decode("utf-8"))
        print("Executing Tilt Commands")
        self.log.info("Executing Tilt Commands")
        # Tilt to Target Tilts

        print(f"Executing Tilt Commands of ha: {self.ha_tilt}, oiii: {self.oiii_tilt}")
        skip = self.hardware_status.get_status(
            which="down", verbose=False, return_units=True
        )
        # Tilt to Target Tilts
        res = AllTiltScienceFilters(
            ha_tilt=self.ha_tilt, oiii_tilt=self.oiii_tilt, skip=skip
        )
        print("Command sent, sleeping 5 to let settle.")
        time.sleep(10)
        continue_on = False
        try_tilt = 3
        while not continue_on:
            print("Checking that Tilts are within tolerance")
            ha_df, oiii_df = AllCheckFilterTilts(self.ha_tilt, self.oiii_tilt)
            nbad_ha = len(ha_df.loc[ha_df.isGood == False])
            nbad_oiii = len(oiii_df.loc[oiii_df.isGood == False])
            all_bad = nbad_ha + nbad_oiii
            if all_bad == 0:
                print("All Filters within tolerance of TiltGoal.")
                continue_on = True
            elif try_tilt > 3:
                print(
                    f"WARNING::: {all_bad} Filters out of tolerance but number of tries (3) reached. Setting these DOWN."
                )
                for bad_ha in list(ha_df.loc[ha_df.isGood == False, "Name"].values):
                    self.hardware_status.MarkUnitDown(bad_ha)
                for bad_oiii in list(
                    oiii_df.loc[oiii_df.isGood == False, "Name"].values
                ):
                    self.hardware_status.MarkUnitDown(bad_oiii)
                continue_on = True
            else:
                try_tilt += 1

                print(f"Warning: {all_bad} Filters are out of tolerence. Trying again.")
                print(ha_df)
                print(oiii_df)
                res = AllTiltScienceFilters(
                    ha_tilt=self.ha_tilt, oiii_tilt=self.oiii_tilt
                )
                time.sleep(10)
        # Execute Dither
        print("Dithering...")
        self.log.info(f"dithering {dither_east} east and {dither_north} north.")
        r = DitherMount(dither_east, dither_north)
        self.log.info(r.stdout.decode("utf-8"))
        # Start Guiding
        print("Starting AutoGuider and sleeping 15 sec")
        self.log.info("Activating Autoguider and sleeping 15 sec.")
        r = StartAutoGuide()
        time.sleep(15)
        self.log.info(r.stdout.decode("utf-8"))
        timeout = self.exptime + 60
        skip = self.hardware_status.get_status(
            which="down", verbose=False, return_units=True
        )
        for i in range(self.niter):
            res = AllScienceExposure(
                exptime=self.exptime,
                off_exptime=self.offband_exptime,
                n_offs=self.n_offs,
                name=self.target,
                timeout_global=timeout,
                skip=skip,
            )
            # self.log.info(res)
        # Stop Guiding
        print("Stopping AutoGuider.")
        self.log.info("Stopping Autoguider.")
        r = StopAutoGuide()
        self.log.info(r.stdout.decode("utf-8"))
        # Execute Dither
        print("Dithering...")
        self.log.info(f"dithering back to target")
        res = SlewMount(self.target)
        self.log.info(r.stdout.decode("utf-8"))
