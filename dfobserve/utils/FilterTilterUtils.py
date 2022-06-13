"""
Utility functions for interacting with the filter tilters via the webserver 
"""
import warnings

warnings.filterwarnings("ignore")
import numpy as np
from dfobserve.utils.NetworkUtils import get_status_df
from dfobserve.webserver import SendWebRequestNB
import pandas as pd
from dfobserve.webserver import WrapDF


def AllTiltScienceFilters(
    ha_tilt: float, oiii_tilt: float, debug: bool = False, **kwargs
):
    """
    Tilt all filters of a given filter type to a specific value.

    Parameters
    ----------
    ha_tilt: float
        amount to tilt Ha filters. Must be between -20 and 20
    oiii_tilt: float
        angle to tilt OIII filters. Must be between -20 and 20
    debug: bool, default: False
        debug flag for testing (executes a dryrun).
    **kwargs: optional
        kwargs recognized by SendWebRequestNB
    """
    ha_command = f"device/filtertilter?command=set&argument={ha_tilt}"
    oiii_command = f"device/filtertilter?command=set&argument={oiii_tilt}"
    if debug:
        res = SendWebRequestNB(
            ha_command=ha_command, oiii_command=oiii_command, dryrun=True, **kwargs
        )
    else:
        res = SendWebRequestNB(
            ha_command=ha_command, oiii_command=oiii_command, **kwargs
        )
    return res


def AllMoveFilters(ha_move: float, oiii_move: float, debug: bool = False, **kwargs):
    """
    Tilt all filters of a given filter type by a specific value.

    Parameters
    ----------
    ha_move: float
        amount to tilt Ha filters. Must be between -20 and 20
    oiii_move: float
        angle to tilt OIII filters. Must be between -20 and 20
    debug: bool, default: False
        debug flag for testing (executes a dryrun).
    **kwargs: optional
        kwargs recognized by SendWebRequestNB
    """
    ha_command = f"device/filtertilter?command=move&argument={ha_move}"
    oiii_command = f"device/filtertilter?command=move&argument={oiii_move}"
    if debug:
        res = SendWebRequestNB(
            ha_command=ha_command, oiii_command=oiii_command, dryrun=True, **kwargs
        )
    else:
        res = SendWebRequestNB(
            ha_command=ha_command, oiii_command=oiii_command, **kwargs
        )
    return res


def TiltFiltersByType(filt_name, tilt_angle):
    pass


def AllGetFilterTilts(which="science", debug=False, **kwargs):
    """
    Gets the tilts for all science filters

    Parameters
    ----------
    which: str, default: 'science'
        which filters to return tilts for. Only science ones *should* be needed.
    """
    command = f"device/filtertilter?command=get"
    if debug == False:
        res = SendWebRequestNB(ha_command=command, oiii_command=command, **kwargs)
    elif debug == True:
        res = SendWebRequestNB(
            ha_command=command, oiii_command=command, dryrun=True, **kwargs
        )
        return res

    # This is a summary object. Let's make a new WrapDF with just the params for FilterTilter
    cols = ["Name", "Filter", "Angle", "RawAngle", "ZeropointAngle"]
    df = pd.DataFrame(columns=cols)
    sdf = get_status_df()
    halpha = list(sdf.loc[sdf.Filter == "ha6647", "Name"])
    oiii = list(sdf.loc[sdf.Filter == "oiii5071", "Name"])
    units = halpha + oiii
    unit_type = ["halpha6647"] * len(halpha) + ["oiii5071"] * len(oiii)
    for i, filt in zip(units, unit_type):
        unit_obj = res.get_response_by_name(i).FilterTilter
        df = df.append(
            {
                "Name": i,
                "Filter": filt,
                "Angle": unit_obj.Angle,
                "RawAngle": unit_obj.RawAngle,
                "ZeropointAngle": unit_obj.ZeropointAngle,
            },
            ignore_index=True,
        )
    return df


def AllCheckFilterTilts(
    ha_tilt: float, oiii_tilt: float, tol: float = 0.3, verbose=False, **kwargs
):
    """
    Query the filter tilters and obtain the current tilt. Check that tilts are within specified tolerance.

    Parameters
    ----------
    ha_tilt: float
        expected tilt for Halpha
    oiii_tilt: float
        expected tilt for [OIII]
    tol: float, default: 0.3
        tolerance between true and expected tilt to return an all OK.

    Returns
    -------
    res: bool
        True if all filters in tolerance, False if not
    bad: list
        List of any filters that returned bad tilts
    """
    command = f"device/filtertilter?command=get"
    res = SendWebRequestNB(
        ha_command=command, oiii_command=command, verbose=False, **kwargs
    )  # Summary obj
    sdf = get_status_df()
    halpha = sdf.loc[sdf.Filter == "ha6647", "Name"].values
    oiii = sdf.loc[sdf.Filter == "oiii5071", "Name"].values
    if "skip" in kwargs.keys():
        halpha = [i for i in halpha if i not in kwargs["skip"]]
        oiii = [i for i in oiii if i not in kwargs["skip"]]

    ha_df = pd.DataFrame(
        columns=["Name", "ha_tiltgoal", "ha_tilt", "ha_diff", "tol", "isGood"]
    )
    oiii_df = pd.DataFrame(
        columns=["Name", "oiii_tiltgoal", "oiii_tilt", "oiii_diff", "tol", "isGood"]
    )
    for i in halpha:
        tilt = res.get_response_by_name(i).FilterTilter.Angle
        diff = np.abs(np.abs(float(tilt)) - np.abs(ha_tilt))
        if diff <= tol:
            isGood = True
        elif diff > tol:
            isGood = False
        ha_df = ha_df.append(
            {
                "Name": i,
                "ha_tiltgoal": ha_tilt,
                "ha_tilt": tilt,
                "ha_diff": diff,
                "tol": tol,
                "isGood": isGood,
            },
            ignore_index=True,
        )

    for i in oiii:
        tilt = res.get_response_by_name(i).FilterTilter.Angle
        diff = np.abs(np.abs(float(tilt)) - np.abs(oiii_tilt))
        if diff <= tol:
            isGood = True
        elif diff > tol:
            isGood = False
        oiii_df = oiii_df.append(
            {
                "Name": i,
                "oiii_tiltgoal": oiii_tilt,
                "oiii_tilt": tilt,
                "oiii_diff": diff,
                "tol": tol,
                "isGood": isGood,
            },
            ignore_index=True,
        )

    if verbose:
        print("H alpha Tilt Checks")
        print(ha_df)
        print("\n")
        print("OIII Tilt Checks")
        print(oiii_df)
    Ngood_ha = len(np.where(ha_df.isGood.values == True)[0])
    Ngood_oiii = len(np.where(oiii_df.isGood.values == True)[0])
    if verbose:
        print(f"{Ngood_ha} H-alpha filters are in tolerance.")
        print(f"{Ngood_oiii} OIII filters are in tolerance.")

    return ha_df, oiii_df


def AllSetTiltsToZero():
    pass
