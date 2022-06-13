import warnings

warnings.filterwarnings("ignore")
from dfobserve.utils.HardwareUtils import HardwareStatus


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
import fire

from dfobserve.webserver import SendWebRequestNB


def AllCheckFocusers(
    movement: int = 1000,
    tolerance: int = 5,
    use_birger: bool = True,
    verbose: bool = False,
    update: bool = True,
    **kwargs,
):
    """
    Check the focusers by moving to a specific value and checking focus
    value is within tolerance, then moving back and checking again.

    Parameters
    ----------
    movement: int, default: 1000
        number of steps to move the focuser
    tolerance: int, default: 5
        number of steps a unit can be off by and still marked 'UP'
    user_birger: bool, default: True
        use the birger focusers
    verbose: bool, default: True
        verbose display of test results
    update: bool, default: True
        whether to actually mark units down in config file if they fail the test.
    **kwargs
        any kwargs recognized by SendWebRequestNB
    """
    hs = HardwareStatus()
    skip = hs.get_status(which="down", verbose=False, return_units=True)
    command = f"calculation/?type=check-focuser&movement={movement}&tolerance={tolerance}&use_birger={use_birger}"

    r = SendWebRequestNB(
        command=command, verbose=False, wait_for_response=False, skip=skip, **kwargs
    )
    with tqdm(total=30) as pbar:
        for i in range(30):
            time.sleep(1)
            pbar.update(1)
    status = SendWebRequestNB(
        command="status", verbose=False, wait_for_response=False, skip=skip, **kwargs
    )

    for i in status.df.index:
        name = status.df.loc[i, "Name"]
        api_res = status.get_response_by_name(name)
        if api_res.Focus.FocuserCheckResult == None:
            print(f"Focuser Check value for {name} is None; Likely a focuser error")
            continue
        if not api_res.Focus.FocuserCheckResult.startswith("success"):
            if api_res.Focus.FocuserCheckResult.startswith("fail"):
                print(
                    f"Unit {name} did not have a successful check. Unit will be marked DOWN."
                )
                if verbose:
                    print(api_res.Focus.FocuserCheckResult)
                if update:
                    hs.MarkUnitDown(name)
            elif api_res.Focus.FocuserCheckResult.startswith("error"):
                print(
                    f"Unit {name} had a focuser communication error. Unit will be marked DOWN."
                )
                if update:
                    hs.MarkUnitDown(name)

    return status


if __name__ == "__main__":
    fire.Fire(AllCheckFocusers)
