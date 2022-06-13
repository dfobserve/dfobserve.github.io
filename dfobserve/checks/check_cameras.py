from asyncio import wait_for
from dfobserve.webserver.WebRequests import SendWebRequestNB
from dfobserve.utils.HardwareUtils import HardwareStatus
import sys
import time
import fire
from tqdm import tqdm


def AllCheckCameras(ntests=10, update=True, **kwargs):
    """
    Runs a Camera Check command via the webserver.

    Parameters
    ----------
    ntests: int, default: 10
        number of tests to run. Each test takes 2 bias images and makes a comparison, and another overarching test uses all frames.
    update: bool, default: True
        whether to actually mark units down based on test results
    **kwargs
        any specific kwargs to pass to SendWebRequestNB
    """
    hs = HardwareStatus()
    skip = hs.get_status(which="down", verbose=False, return_units=True)
    print(f"Running Camera tests with {ntests} tests.")
    command = f"calculation?type=check-camera&ntests={ntests}"
    res = SendWebRequestNB(
        command,
        which="all",
        skip=skip,
        verbose=False,
        wait_for_response=False,
        **kwargs,
    )
    for i in res.df.index:
        res_summary = res.df.loc[i, "full_response"]
        if res_summary == 0:
            print(
                f"HTTPError, Unknown command. Unit {res.df.loc[i,'Name']} will be Marked Down."
            )
            hs.MarkUnitDown(res.df.loc[i, "Name"])
        elif res_summary == 1:
            print(f"URLError. Unit {res.df.loc[i,'Name']} will be Marked Down.")
            hs.MarkUnitDown(res.df.loc[i, "Name"])
        elif res_summary == 2:
            print(f"Unknown Error. Unit {res.df.loc[i,'Name']} will be Marked Down.")
            hs.MarkUnitDown(res.df.loc[i, "Name"])

    wait = ntests * 8
    print(f"Waiting for Cameras to Run Tests ({wait} s).")
    with tqdm(total=wait) as pbar:
        for i in range(wait):
            time.sleep(1)
            pbar.update(1)

    print("Assessing Checks for units with responses.")

    status = SendWebRequestNB(
        "status",
        which="all",
        skip=hs.get_status(which="down", verbose=False, return_units=True),
        verbose=False,
        wait_for_response=False,
    )
    for i in status.df.index:
        api_res = status.get_response_by_name(status.df.loc[i, "Name"])
        if api_res.Activity.CalculationInProgress:
            print(
                f"Camera Server for {status.df.loc[i,'Name']} is taking too long to run its test. Machine will be marked DOWN."
            )
            if update:
                hs.MarkUnitDown(status.df.loc[i, "Name"])
        elif api_res.XtraCalculations.CalculationErrorHasOccurred:
            print(
                f"The Calculation {status.df.loc[i,'Name']} for encountered an error. Machine will be marked DOWN."
            )
            if update:
                hs.MarkUnitDown(status.df.loc[i, "Name"])

        elif api_res.CameraProperties.Bias != "Acceptable":
            print(
                f"The Bias for {status.df.loc[i,'Name']} was not acceptable. Machine will be marked DOWN."
            )
            if update:
                hs.MarkUnitDown(status.df.loc[i, "Name"])
        elif api_res.CameraProperties.ReadNoise != "Acceptable":
            print(
                f"The ReadNoise for {status.df.loc[i,'Name']} was not acceptable. Machine will be marked DOWN."
            )
            if update:
                hs.MarkUnitDown(status.df.loc[i, "Name"])

    return status


if __name__ == "__main__":
    fire.Fire(AllCheckCameras)
