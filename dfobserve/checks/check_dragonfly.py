import warnings

warnings.filterwarnings("ignore")
from dfobserve.utils.HardwareUtils import HardwareStatus


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
import fire
import subprocess as sp
from dfobserve.webserver import SendWebRequestNB
import re
from dfobserve.checks import AllCheckCameras, AllCheckFilterTilters, AllCheckFocusers


def AllCheckDragonfly(
    skip: list = [],
    update: bool = True,
    camera_kwargs: dict = {},
    filtertilter_kwargs: dict = {},
    focuser_kwargs: dict = {},
):
    """
    Check the health of the DFNB system and mark pis down if needed.

    Parameters
    ----------
    skip: list, default: []
        List of tests to skip along the way. Options include 'mount','network','focusers','filters','cameras'
    update: bool, default: True
        Whether to update the config file with the results of each test (i.e., actually mark the pis down).
    camera_kwargs: dict, default: {}
        keyword arguments accepted by AllCheckCameras to modify the nature of the tests run.
    filtertilter_kwargs: dict, default: {}
        keyword arguments accepted by AllCheckFilterTiters to modify the nature of the tests run.
    focuser_kwargs: dict, default: {}
        keyword arguments accepted by AllCheckFocusers to modify the nature of the tests run.
    """

    # Test Mount

    if "mount" not in skip:
        print("Testing the operation of the mount.")
        command = "CheckMount -v"
        mountTimeout = 600
        try:
            res = sp.run(command, shell=True, capture_output=True, timeout=mountTimeout)
            stdout = res.stdout.decode("utf-8")
            sdterr = res.stderr.decode("utf-8")
            if re.search(r"Mounts OK", stdout):
                print(stdout.strip())
            else:
                print("Mount Error.")
        except:
            print("Mount Check Unsuccessful. Mount Error.")

    hs = HardwareStatus()
    if "network" not in skip:
        print("Initializing Hardware Current Status File.")
        hs.InitializeHardwareStatus()
        # Ping Sticks and see which are accessible
        print("Pinging Pis over webserver to see which are accessible")
        hs.MarkAccessibleUnitsUp()
        down_units = hs.get_status(which="down", verbose=False, return_units=True)
        if len(down_units) > 0:
            user_in = input("Some Pis are down. Attempt to reconnect? [Y/n]: ")
            if user_in in ["y", "Y", "yes", "Yes", "YES", ""]:
                # Try to start docker daemon and pi server
                for i in down_units:
                    command1 = f"ssh {i} sudo dockerd &"
                    command2 = f"ssh {i} sudo docker-compose up -d"
                    print(f"Attempting to start docker daemon and server on {i}")
                    r1 = sp.run(command1, shell=True, capture_output=True)
                    print(r1.stdout.decode("utf-8"))
                    r2 = sp.run(command2, shell=True, capture_output=True)
                    print(r2.stdout.decode("utf-8"))
    else:
        print("Warning, running without initializing hardware status file.")

    # Check other aspects. Will automatically skip DOWN units, and mark additional units down as they fail.

    # Focusers
    if "focusers" not in skip:
        print("----------------------")
        print("Checking the Focusers.")
        print("----------------------")
        focus_status = AllCheckFocusers(update=update, **focuser_kwargs)

    # Cameras
    if "cameras" not in skip:
        print("----------------------")
        print("Checking the Cameras.")
        print("----------------------")
        camera_status = AllCheckCameras(update=update, **camera_kwargs)

    # Filter Tilters
    if "filters" not in skip:
        print("----------------------------")
        print("Checking the Filter Tilters.")
        print("----------------------------")
        filter_status = AllCheckFilterTilters(update=update, **filtertilter_kwargs)

    # Summary:
    print("-------------------------------")
    print("   Summary of Results    ")
    print("-------------------------------")
    print("Map of Up/Down Units. \n")
    up = hs.get_status(which="up", verbose=False, return_units=True)
    down = hs.get_status(which="down", verbose=False, return_units=True)
    upcolor = "\033[32m"
    downcolor = "\033[31m"
    conv = {}
    for i in range(301, 311):
        if f"Dragonfly{i}" in up:
            conv[f"Dragonfly{i}"] = f"{upcolor}DF-{i}"
        elif f"Dragonfly{i}" in down:
            conv[f"Dragonfly{i}"] = f"{downcolor}DF-{i}"
    layout = f"""
    {conv['Dragonfly301']}  {conv['Dragonfly302']}  {conv['Dragonfly303']}

{conv['Dragonfly304']}  {conv['Dragonfly305']}  {conv['Dragonfly306']}  {conv['Dragonfly307']}
    
    {conv['Dragonfly308']}  {conv['Dragonfly309']}  {conv['Dragonfly310']} \n \n"""
    # Print cool map.

    print(layout)
    final_status = SendWebRequestNB("status", verbose=False)
    return final_status  # This is a status WebRequest which should have basically everything.


if __name__ == "__main__":
    fire.Fire(AllCheckDragonfly)
