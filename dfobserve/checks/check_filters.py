"""
Module for testing that filters are healthy and behaving normally. 
Check executes several tilt commands and confirms that the filters return angles that are within tolerance. 
"""
import warnings

from dfobserve.utils.HardwareUtils import HardwareStatus

warnings.filterwarnings("ignore")
from dfobserve.utils.FilterTilterUtils import (
    AllCheckFilterTilts,
    AllMoveFilters,
    AllTiltScienceFilters,
    AllGetFilterTilts,
)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from tqdm import tqdm

plt.ion()

import fire


def AllCheckFilterTilters(
    tol: float = 0.3,
    update: bool = True,
    check_angles: list = [5, 0],
    verbose: bool = True,
    plot: bool = False,
    save_plot: bool = False,
    save_plot_name: str = "FilterTilterChecks.png",
):
    """
    Confirm that Tilters are not stuck and are moving well.

    Parameters
    ----------
    tol: float, defaut: 0.3
        tolerance desired between actual tilt and input tilt.
    update: bool, default: True
        whether to actually mark units down in the config file based on test results.
    check_angles: list, default: [5,0]
        angles to move to and confirm unit tilts are within tolerance.
    verbose: bool, default: True
        Full outputs when running the check.
    plot: bool, default: False
        plot up the results of the difference between tilt goal and tilts for all units at each check angle
    save_plot: bool, default: False
        whether to save a plot to disk
    save_plot_name: str, default: 'FilterTilterChecks.png'
        path/name to save file to disk.
    """
    if verbose:
        print(f"Cycling Tilts And Checking Diffs...")
    ha_diffs = []
    oiii_diffs = []
    hs = HardwareStatus()
    skip = hs.get_status(which="down", verbose=False, return_units=True)
    if verbose:
        all_bad = []
        for angle in check_angles:
            print(f"Testing Theta = {angle} with tolerance {tol}")
            print("Tilting filters and sleeping 10s.")
            res = AllTiltScienceFilters(angle, angle, verbose=False, skip=skip)
            time.sleep(10)
            check_ha, check_oiii = AllCheckFilterTilts(
                angle, angle, tol=tol, verbose=False, skip=skip
            )
            bad = len(check_ha.loc[check_ha.isGood == False]) + len(
                check_oiii.loc[check_oiii.isGood == False]
            )

            print("------------------------")
            print(f"N Bad: {bad}")
            print("------------------------")
            print(check_ha)
            print(check_oiii)
            badlist = list(
                check_ha.loc[check_ha.isGood == False, "Name"].values
            ) + list(check_oiii.loc[check_oiii.isGood == False, "Name"].values)
            for i in badlist:
                if i not in all_bad:
                    all_bad.append(i)
                    if update:
                        hs.MarkUnitDown(i)
            ha_diffs.append(check_ha.ha_diff.values)
            oiii_diffs.append(check_oiii.oiii_diff.values)
        if len(all_bad) > 0:
            print(
                "The following units had tilts out of tolerance and were marked down:"
            )
            for i in all_bad:
                print(i)
        else:
            print("All Units Tested were found to be within tolerance.")
    else:
        with tqdm(total=10 * len(check_angles)) as pbar:
            all_bad = []
            for angle in check_angles:
                res = AllTiltScienceFilters(angle, angle, verbose=False, skip=skip)
                for i in range(10):
                    time.sleep(1)
                    pbar.update(1)
                check_ha, check_oiii = AllCheckFilterTilts(
                    angle, angle, tol=tol, verbose=False, skip=skip
                )
                bad = len(check_ha.loc[check_ha.isGood == False]) + len(
                    check_oiii.loc[check_oiii.isGood == False]
                )
                badlist = list(
                    check_ha.loc[check_ha.isGood == False, "Name"].values
                ) + list(check_oiii.loc[check_oiii.isGood == False, "Name"].values)
                for i in badlist:
                    if i not in all_bad:
                        all_bad.append(i)
                        if update:
                            hs.MarkUnitDown(i)
                ha_diffs.append(check_ha.ha_diff.values)
                oiii_diffs.append(check_oiii.oiii_diff.values)
        if len(all_bad) > 0:
            print(
                "The following units had tilts out of tolerance and were marked down:"
            )
            for i in all_bad:
                print(i)
        else:
            print("All Units Tested were found to be within tolerance.")
    if plot:
        fig, ax = plt.subplots(figsize=(16, 4))
        for n, i in enumerate(check_angles):
            y = np.array(ha_diffs[n])
            x = np.array([i] * len(y))
            if n == 0:
                ax.plot(
                    x, y, "o", color="C0", ms=11, mec="k", alpha=0.7, label="Halpha"
                )
            else:
                ax.plot(
                    x,
                    y,
                    "o",
                    color="C0",
                    ms=11,
                    mec="k",
                    alpha=0.7,
                )
            y = np.array(oiii_diffs[n])
            x = np.array([i] * len(y))
            if n == 0:
                ax.plot(x, y, "s", color="C1", ms=11, mec="k", alpha=0.7, label="OIII")
            else:
                ax.plot(x, y, "s", color="C1", ms=11, mec="k", alpha=0.7)
        ax.legend()
        ax.set_xlabel("Tilt Goals")
        ax.set_ylabel("Tilt Differential (Goal - Actual)")
        ax.set_ylim(-1, 1)
        ax.axhline(0.0, color="k")
        ax.axhline(tol, color="gray", alpha=0.5)
        ax.axhline(-tol, color="gray", alpha=0.5)
        if save_plot:
            fig.savefig(save_plot_name)
        plt.show()


if __name__ == "__main__":
    fire.Fire(AllCheckFilterTilters)
