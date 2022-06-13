"""
FlipFlatUtils: Functions to open/close all or a subset of flip flats using the web server.
"""
import numpy as np
import os
import subprocess as sp
import pandas as pd
from .NetworkUtils import get_status_df
from ..webserver import SendWebRequestNB

__all__ = ["AllCloseFlipFlats", "AllOpenFlipFlats", "OpenFlipFlats", "CloseFlipFlats"]


def AllTurnOnFlipFlaps(
    lampbrightness: int = 60,
    port: str = "/dev/ttyUSB2",
    **kwargs,
):
    """
    Turn on all the flip flats for units that have flats.

    Parameters
    ----------
    lampbrightness: int, default: 60
        illumination to set the flip flats to.
    port: str, default: '/dev/ttyUSB2'
        port where the flip flat is plugged in.
    """
    command = f"device/flipflat?command={lampbrightness}&port={port}"
    response = SendWebRequestNB(all_flathaving_command=command, **kwargs)
    return response


def AllTurnOffFlipFlaps(
    verbose: bool = True, which: str = "science", port: str = "/dev/ttyUSB2", **kwargs
):
    """
    Turn on all the flip flats
    """
    command = f"device/flipflat?command=off&port={port}"
    response = SendWebRequestNB(
        command=command, which=which, all_flathaving_command=command, **kwargs
    )
    return response


def AllCloseFlipFlats(
    verbose=True, which="science", port: str = "/dev/ttyUSB2", **kwargs
):
    """
    Parameters
    ----------
    verbose: bool (optional)
        whether to show the return from the webrequest. Default: True
    **kwargs: (optional)
        additional keyword arguments recognized by SendWebRequestNB
    """
    command = f"device/flipflat?command=close&port={port}"
    result = SendWebRequestNB(all_flathaving_command=command, **kwargs)
    if verbose:
        print(result)
    return result


def AllOpenFlipFlats(
    verbose=True, which="science", port: str = "/dev/ttyUSB2", **kwargs
):
    """
    Parameters
    ----------
    verbose: bool (optional)
        whether to show the return from the webrequest. Default: True
    **kwargs: (optional)
        additional keyword arguments recognized by SendWebRequestNB
    """
    command = f"device/flipflat?command=open&port={port}"
    result = SendWebRequestNB(all_flathaving_command=command, **kwargs)
    if verbose:
        print(result)
    return result


def OpenFlipFlats(
    unit_list: list,
    port: str = "/dev/ttyUSB2",
    verbose: bool = True,
):
    """
    Open only SOME flip flats. Does them one by one at the moment

    Parameters
    ----------
    unit_list: list
        list of units to open flip flats for. Can be in form [301,303,309] or ['Dragonfly301','Dragonfly306']
    verbose: bool (optional)
        whether to show the return from the webrequest. Default: True
    """
    df = get_status_df()
    if not unit_list[0].startswith("Dragonfly"):
        unit_list = ["Dragonfly" + str(i) for i in unit_list]
    command_prefix = "python3 C:/Dragonfly/Programs/SendWebRequest.py -w "
    for i in unit_list:
        command_suffix = f"SendWebRequest http://{df.loc[df.name==i,'IP']}:3000/api/device/flipflat?command=open&r&port={port}"
        command = command_prefix + command_suffix
        result = sp.run(command, shell=True, capture_output=True, text=True)
    if verbose:
        print(result)
    return result


def CloseFlipFlats(unit_list: list, port: str = "/dev/ttyUSB2", verbose: bool = True):
    """
    Close only SOME flip flats. Currently does them one by one.

    Parameters
    ----------
    unit_list: list
        list of units to open flip flats for. Can be in form [301,303,309] or ['Dragonfly301','Dragonfly306']
    verbose: bool (optional)
        whether to show the return from the webrequest. Default: True
    """
    df = get_status_df()
    if not unit_list[0].startswith("Dragonfly"):
        unit_list = ["Dragonfly" + str(i) for i in unit_list]
    command_prefix = "python3 C:/Dragonfly/Programs/SendWebRequest.py -w "
    for i in unit_list:
        command_suffix = f"http://{df.loc[df.name==i,'IP']}:3000/api/device/flipflat?command=close&port={port}"
        command = command_prefix + command_suffix
        result = sp.run(command, shell=True, capture_output=True, text=True)
    if verbose:
        print(result)
    return result
