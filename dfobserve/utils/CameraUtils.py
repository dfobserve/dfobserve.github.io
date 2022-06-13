"""
Utility functions for interacting with the cameras.
"""
import warnings

warnings.filterwarnings("ignore")
import pandas as pd

import numpy as np

from dfobserve.utils.NetworkUtils import get_status_df
from ..webserver import SendWebRequestNB
from .FlipFlatUtils import (
    AllCloseFlipFlats,
    AllOpenFlipFlats,
    AllTurnOffFlipFlaps,
    AllTurnOnFlipFlaps,
)
import time

from dfobserve.utils.SkyXUtils import GetMountPointing


def AllScienceExposure(
    exptime: int,
    off_exptime: int,
    n_offs: int,
    oh_exptime: int = None,
    extras: dict = None,
    wait_readout: int = 60,
    debug: bool = False,
    **kwargs,
):
    """
    Execute a standard science exposure
    """
    command = f"expose?type=light"

    science_command = command + f"&time={exptime}"
    offs_command = command + f"&time={off_exptime}&n={n_offs}"
    if isinstance(oh_exptime, int):
        oh_command = command + f"&time={oh_exptime}"
    else:
        oh_command = science_command

    if extras is not None:
        for key in extras.keys():
            science_command += f"&{key}={extras[key]}"
            offs_command += f"&{key}={extras[key]}"
            oh_command += f"&{key}={extras[key]}"

    d = GetMountPointing()
    for key in d.keys():
        science_command += f"&{key}={d[key]}"
        offs_command += f"&{key}={d[key]}"
        oh_command += f"&{key}={d[key]}"

    timeout = exptime + wait_readout
    if debug:
        response = SendWebRequestNB(
            command=science_command,
            which="science",
            ha_off_command=offs_command,
            oiii_off_command=offs_command,
            OH_command=oh_command,
            OH_off_command=oh_command,
            timeout_global=timeout,
            dryrun=True,
            **kwargs,
        )
    else:
        response = SendWebRequestNB(
            command=science_command,
            which="science",
            ha_off_command=offs_command,
            oiii_off_command=offs_command,
            OH_command=oh_command,
            OH_off_command=oh_command,
            timeout_global=timeout,
            verbose=False,
            request_type="exposure",
            readout_time=wait_readout,
            **kwargs,
        )
    return response


def AllExpose(
    exptime: int,
    which: str = "all",
    extras: dict = None,
    wait_readout: int = 60,
    **kwargs,
):
    """
    Very Simply, take an exposure on a certain set of cameras.

    Parameters
    ----------
    exptime: int
        exposure time in seconds
    which: str (optional)
        which cameras to send to. Options include
            `'all'`: send to all lenses. (for example, make all lenses take a 0 second exposure) \n
            `'science'`: send to the H-alpha and OIII lenses only. All others will idle. \n
            `'science offs'`: send to the offs for H-alpha and OIII only. \n
            `'OH'`: send command to the OH on and OH off units
            `'halpha'`: send to halpha units only
            `'oiii'`: send to the OIII units only
        (Default: 'all')
    wait_readout: int (optional)
        how long to wait in seconds for the exposure to read out before disconnecting.
    """
    timeout = exptime + wait_readout
    command = f"expose?type=light&time={exptime}"
    if extras is not None:
        for key in extras.keys():
            command += f"&{key}={extras[key]}"
    d = GetMountPointing()
    for key in d.keys():
        command += f"&{key}={d[key]}"

    response = SendWebRequestNB(
        command=command,
        which=which,
        timeout_global=timeout,
        verbose=False,
        request_type="exposure",
        readout_time=wait_readout,
        **kwargs,
    )
    return response


def AllFlatFieldExposure(
    exptime: int,
    n: int = 1,
    which: str = "science",
    extras=None,
    wait_readout: int = 60,
    **kwargs,
):
    """
    Take a flatfield using all the science filters. (or some other set)
    """
    command = f"expose?type=flat&time={exptime}&n={n}"
    d = GetMountPointing()
    for key in d.keys():
        command += f"&{key}={d[key]}"
    if extras is not None:
        for key in extras.keys():
            command += f"&{key}={extras[key]}"
    timeout = exptime + wait_readout
    response = SendWebRequestNB(
        command=command,
        which=which,
        timeout_global=timeout,
        request_type="exposure",
        readout_time=wait_readout,
        **kwargs,
    )
    return response


def AllDarkExposure(
    exptime: int, which: str = "all", extras=None, wait_readout: int = 60, **kwargs
):
    """
    Take a dark exposure.
    """
    command = f"expose?type=dark&time={exptime}"
    d = GetMountPointing()
    for key in d.keys():
        command += f"&{key}={d[key]}"
    if extras is not None:
        for key in extras.keys():
            command += f"&{key}={extras[key]}"
    timeout = exptime + wait_readout
    response = SendWebRequestNB(
        command=command,
        which=which,
        timeout_global=timeout,
        request_type="exposure",
        readout_time=wait_readout,
        **kwargs,
    )
    return response


def AutoFocus(
    exptime: int = 3,
    focus_lower: float = 1000,
    focus_upper: float = 1000,
    nsteps: int = 25,
    use_sextractor: bool = True,
    use_birger: bool = True,
    non_adaptive: bool = True,
    fit: bool = True,
    extras=None,
    **kwargs,
):
    command = f"autofocus?time={exptime}&focus_lower={focus_lower}&focus_upper={focus_upper}&nsteps={nsteps}&use_sextractor={use_sextractor}&use_birger={use_birger}&non_adaptive={non_adaptive}&fit={fit}"
    if extras is not None:
        for key in extras.keys():
            command += f"&{key}={extras[key]}"
    r = SendWebRequestNB(command=command, which="all", **kwargs)
    return r


def AllSetCameraTemperatures(temperature: float, which: str = "all", **kwargs):
    if temperature < 15:
        command = f"device/cooler?command=set&temp={temperature}"
    elif "disable" in kwargs.keys():
        command = f"device/cooler?command=disable"
    elif temperature > 15:
        command = f"device/cooler?command=disable"
    r = SendWebRequestNB(command=command, which=which, **kwargs)
    return r


def AllCheckCameraTemperatures(
    temperature: float,
    which: str = "all",
    tol: float = 5,
    verbose: bool = True,
    **kwargs,
):
    command = f"device/cooler?command=get"
    r = SendWebRequestNB(command=command, which=which, **kwargs)
    # confirm temps within tolerance
    sdf = get_status_df()
    df_units = list(sdf.Name.values)
    temp_df = pd.DataFrame(
        columns=["Name", "ExpectedTemp", "CurrentTemp", "absdiff", "tol", "isGood"]
    )
    temp_df.tol = tol
    for i in df_units:
        api_res = r.get_response_by_name(i)
        camera_temp = api_res.CameraProperties.CurrentTemperature
        abs_diff = np.abs(np.abs(temperature) - np.abs(camera_temp))
        if abs_diff <= tol:
            isGood = True
        else:
            isGood = False
        temp_df = temp_df.append(
            {
                "Name": i,
                "ExpectedTemp": temperature,
                "CurrentTemp": camera_temp,
                "absdiff": abs_diff,
                "isGood": isGood,
            },
            ignore_index=True,
        )
    bad = len(temp_df.loc[temp_df.isGood == False])
    if verbose:
        print("----------")
        print(f"BAD: {bad}")
        print("----------")
        print(temp_df)
    return temp_df, bad
