"""
Tools for getting information about the network of raspberry pis.
"""

import os
import re
import pandas as pd
import subprocess as sp
import io
import numpy as np

__all__ = ["get_network_df", "get_status_df", "get_config_df"]


def get_network_df(
    net_path: str = "/mnt/c/Windows/System32/net.exe", verbose: bool = False
) -> pd.DataFrame:
    """
    Obtains the ip addresses of the pis and returns a dataframe.

    Parameters
    ----------
    net_path: str (optional)
        path to the net.exe
    verbose: bool (optional)
        whether to display the dataframe (default: False)

    Returns
    -------
    network_df: pandas.DataFrame
        df containing the ip addresses, mount volumes, etc.
    """
    network_call = sp.run(
        rf"{net_path} use | head -n -2 | tail -n +4",
        shell=True,
        capture_output=True,
        text=True,
    )
    network_call = re.sub(r"-+\n", r"", network_call.stdout.replace("\n\n", "\n"))
    network_call = re.sub(r"\n?\s+M", r"\t\tM", network_call)
    network_call = re.sub(r"\s{2,}", r",", network_call)
    df = pd.read_csv(io.StringIO(network_call), sep=",")
    print(df)
    df["IP"] = [i.split("\\")[1] for i in df.Remote]
    if verbose:
        print(df)
    return df


def get_status_df(
    hardware_config_path="/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_TEMPLATE.txt",
    verbose=False,
) -> pd.DataFrame:
    """
    Return a dataframe with the current up/down info and IP addresses of each pi

    Parameters
    ----------
    hardware_config_path: str (optional)
        location of the hardware config file
    verbose: bool (optional)
        whether to display the read-in dataframe (default: False)

    Returns
    -------
    status_df: pandas.DataFrame
        df containing IP addresses and UP/Down status (and other info)
    """
    df = pd.read_csv(
        hardware_config_path,
        delim_whitespace=True,
        names=["IP", "Name", "something", "something2", "TempModel", "Filter"],
        dtype=str,
    )
    if verbose:
        print(df)
    return df
