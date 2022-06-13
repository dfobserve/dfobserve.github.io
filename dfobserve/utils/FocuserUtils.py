"""
Utility functions for interacting with the cameras.
"""
import warnings

from dfobserve.webserver.WebRequests import SendWebRequestNB
from dfobserve.utils.NetworkUtils import get_status_df

warnings.filterwarnings("ignore")
import pandas as pd

import numpy as np


def InitFocusers(which="all", verbose=False, **kwargs):
    command = "focuser?command=init"
    r = SendWebRequestNB(command=command, which=which, verbose=verbose, **kwargs)
    return r


def FocuserStatus(which="all", verbose=False, **kwargs):
    command = "focuser?command=status"
    r = SendWebRequestNB(command=command, which=which, verbose=verbose, **kwargs)
    return r


def SetFocus(focus_val, which="all", verbose=False, **kwargs):
    """
    Set the focus of some or all of the units.
    """
    command = f"focuser?command=goto&argument={focus_val}"
    if isinstance(which, list):
        use_list = which
        sdf = get_status_df()
        names = list(sdf.Name.values)
        skip = [i for i in names if i not in use_list]
        r = SendWebRequestNB(
            command=command, which="all", skip=skip, verbose=verbose, **kwargs
        )
    else:
        r = SendWebRequestNB(command=command, which=which, verbose=verbose, **kwargs)
    return r
