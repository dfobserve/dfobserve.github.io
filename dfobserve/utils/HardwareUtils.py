import pandas as pd
import fire
import os
from dfobserve.webserver import SendWebRequestNB


class HardwareStatus:
    def __init__(
        self,
        status_file="/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_CURRENT_STATUS.csv",
    ):
        self.status_file = status_file

    def InitializeHardwareStatus(self):
        df = pd.DataFrame(columns=["Name", "Status"])
        df["Name"] = [f"Dragonfly{i}" for i in range(301, 311)]
        df["Status"] = "UNDETERMINED"
        df.to_csv(self.status_file, index=False)
        return

    def MarkUnitDown(self, unit):
        if not isinstance(unit, str):
            raise AssertionError("Input must be String")
        elif not unit.startswith("Dragonfly"):
            raise AssertionError("Input must be in form DragonflyXXX")
        if not os.path.exists(self.status_file):
            self.InitializeHardwareStatus()
        status = pd.read_csv(self.status_file, header=0)
        status.loc[status.Name == unit, "Status"] = "DOWN"
        status.to_csv(self.status_file, index=False)
        return

    def MarkUnitUp(self, unit):
        if not isinstance(unit, str):
            raise AssertionError("Input must be String")
        elif not unit.startswith("Dragonfly"):
            raise AssertionError("Input must be in form DragonflyXXX")
        if not os.path.exists(self.status_file):
            self.InitializeHardwareStatus()
        status = pd.read_csv(self.status_file, header=0)
        status.loc[status.Name == unit, "Status"] = "UP"
        status.to_csv(self.status_file, index=False)
        return

    def MarkAccessibleUnitsUp(self):
        res = SendWebRequestNB("status", verbose=False)
        units_up = list(res.df.loc[res.df.response_summary == "SUCCESS", "Name"])
        print(
            "The Following Units were accessible via the web server and will be marked UP."
        )
        for i in units_up:
            print(i)
            self.MarkUnitUp(i)
        units_down = list(res.df.loc[res.df.response_summary != "SUCCESS", "Name"])
        print(
            "The Following Units were NOT accessible via the web server and will be marked DOWN."
        )
        for i in units_down:
            print(i)
            self.MarkUnitDown(i)
        if len(units_down) == 0:
            print("NONE. ALL UNITS ARE ACCESSIBLE.")
        return

    def MarkAllUnitsUp(
        self,
    ):
        if not os.path.exists(self.status_file):
            self.InitializeHardwareStatus()
        status = pd.read_csv(self.status_file, header=0)
        status["Status"] = "UP"
        status.to_csv(self.status_file, index=False)

    def MarkAllUnitsDown(
        self,
    ):
        if not os.path.exists(self.status_file):
            self.InitializeHardwareStatus()
        status = pd.read_csv(self.status_file, header=0)
        status["Status"] = "Down"
        status.to_csv(self.status_file, index=False)

    def get_status(self, which="all", verbose=True, return_units=True):
        status = pd.read_csv(self.status_file, header=0)
        up = status.loc[status.Status == "UP"]
        up = up.reset_index(drop=True)
        if len(up) == 0:
            up = []
        else:
            up = list(up["Name"].values)
        down = status.loc[status.Status == "DOWN"]
        down = down.reset_index(drop=True)
        if len(down) == 0:
            down = []
        else:
            down = list(down["Name"].values)
        if "UNDETERMINED" in list(status.Status.values):
            print("Some Units Marked UNDETERMINED. Did you run AllCheckDragonfly?")
        if which == "all":
            if verbose:
                print(status)
            if return_units:
                return status
        elif which.upper() == "UP":

            if verbose:
                print("The following units are UP")
                for i in up:
                    print(i)
            if return_units:
                return up
        elif which.upper() == "DOWN":
            if verbose:
                print("The following units are DOWN")
                for i in down:
                    print(i)
            if return_units:
                return down
        elif which.upper() == "VIZ":
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
        else:
            raise AssertionError("which must be all, up, or down, or viz")


if __name__ == "__main__":
    fire.Fire(HardwareStatus)
