"""
Functions for Using the Webserver to interact with the instrument.
"""

import urllib.request, urllib.error, urllib.parse
import json

import time

from datetime import datetime
import os
from urllib.parse import urlparse

from tqdm import tqdm

import pandas as pd
import requests
from ..utils.NetworkUtils import get_status_df


__all__ = [
    "SendCommand",
    "SendWebRequestNB",
    "Status",
    "NewSendCommand",
    "ParseResponse",
    "APIResponse",
    "WebRequestSummary",
    "WrapDF",
]


def printHeader(hdr):
    colnum = 1
    for col in hdr:
        print("#      %3d   %s" % (colnum, col))
        colnum = colnum + 1


# def SWRTAErrorHandler(signum, frame):
#    print(f"In error handler. Signal {signum} received")
#    os._exit(1)


def NewSendCommand(command: str, ip: str, port=3000, params: dict = {}, timeout=(5, 5)):
    try:
        r = requests.get(
            f"http://{ip}:{port}/api/{command}", params=params, timeout=timeout
        ).json()
        return r
    except requests.ConnectionError:
        return "ConnectionError"
    except requests.HTTPError:
        return "HTTPError"
    except requests.RequestException:
        return "RequestException"
    except requests.ConnectTimeout:
        return "ConnectTimeout"
    except requests.ReadTimeout:
        return "ReadTimeout"
    except requests.Timeout:
        return "Timeout"
    except:
        return "Unknown Exception"


class Status:
    def __init__(self, unit):
        """
        Wrapper for status response from instrument
        """
        if isinstance(unit, str):
            try:
                unit_num = int(unit.upper().split("DRAGONFLY")[1])
            except:
                print("unit as string must by dragonflyXXX or DRAGONFLYXX")
                return
        elif isinstance(unit, int):
            unit_num = unit
        ip_num = unit_num - 290
        ip = f"192.168.50.{ip_num}"
        self.response = NewSendCommand("status", ip=ip)
        if isinstance(self.response, str):
            print(f"Error: {self.response}")
        else:
            self.result = self.response["Result"]
            self.IP = self.response["IPAddress"]
            self.construct_dataframes()
            self.response_fields = [
                "Activity",
                "CameraProperties",
                "CurrentExposure",
                "LastExposure",
                "Focus",
                "Extras",
                "FlipFlat",
                "FilterTilter",
            ]

    def __repr__(self):
        return f"Status Response for Unit at IP: {self.IP} \n Accessible Fields: \n {self.response_fields}"

    def __str__(self):
        return f"Status Response for Unit at IP: {self.IP} \n Accessible Fields: \n {self.response_fields}"

    def construct_dataframes(self):
        self.Activity = pd.DataFrame.from_dict(
            self.response["Activity"], orient="index"
        )
        self.CameraProperties = pd.DataFrame.from_dict(
            self.response["CameraProperties"], orient="index"
        )
        self.CurrentExposure = pd.DataFrame.from_dict(
            self.response["CurrentExposure"], orient="index"
        )
        self.LastExposure = pd.DataFrame.from_dict(
            self.response["LastExposure"], orient="index"
        )
        self.Focus = pd.DataFrame.from_dict(self.response["Focus"], orient="index")
        self.Extras = pd.DataFrame.from_dict(
            self.response["XtraCalculations"], orient="index"
        )
        self.FlipFlat = pd.DataFrame.from_dict(
            self.response["FlipFlat"], orient="index"
        )
        self.FilterTilter = pd.DataFrame.from_dict(
            self.response["FilterTilter"], orient="index"
        )


def SendCommand(
    command: str,
    ip: str,
    timeout_seconds: int = 10,
    name: str = None,
    verbose: bool = False,
):

    url = f"http://{ip}:3000/api/{command}"
    if verbose:
        print(f"Sending command: {url}")
    try:
        response = urllib.request.urlopen(url, timeout=timeout_seconds)
        content = response.read()
        if verbose:
            print(f"Received: {content}")
        return ip, content
    except urllib.error.HTTPError as e:
        if verbose:
            print(f"Unknown command {command} on machine {ip} ({name})")
        return ip, 0

    except urllib.error.URLError:
        if verbose:
            print(f"Machine {ip} ({name}) is offline")
        return ip, 1

    except:
        if verbose:
            print(f"Machine {ip} ({name}) had an unknown exception")
        return ip, 2


def SendWebRequestNB(
    command: str = None,
    which: str = "all",
    skip: list = [],
    ha_command: str = None,
    oiii_command: str = None,
    ha_off_command: str = None,
    oiii_off_command: str = None,
    OH_command: str = None,
    OH_off_command: str = None,
    all_flathaving_command: str = None,
    verbose: bool = True,
    wait_for_response: bool = True,
    timeout_global: int = 120,
    timeout_seconds: int = 10,
    dryrun=False,
    hardware_config_file=None,
    **kwargs,
):
    """
    Send a webrequest to the array but divy up commands by type if requested.
    No required inputs, but if it is run with no inputs, a webrequest will not be sent.

    Parameters
    ----------
    command: str, optional
        command to broadcast to units. This option acts in concert with the `which` keyword argument,
        which determines where the command will be sent. If further separate commands are needed, use
        the individually coded keywords. (Default: None)
    which: str, optional
        which units to broadcast the `command` to. Options include
            `'all'`: send to all lenses. (for example, make all lenses take a 0 second exposure) \n
            `'science'`: send to the H-alpha and OIII lenses only. All others will idle. \n
            `'science offs'`: send to the offs for H-alpha and OIII only. \n
            `'OH'`: send command to the OH on and OH off units
            `'halpha'`: send to halpha units only
            `'oiii'`: send to the OIII units only
        Note that the supplication of any of the more specific keyword args (e.g., `OH_command`) will
        overwrite the command being sent when this option is used. (Default: 'all')
    skip: list, default: []
        any units to skip when sending this command (e.g., those that are down). Should be list of str like 'Dragonfly301'
    ha_command: str, optional
        command to send only to the Halpha units. (Default: None)
    oiii_command: str, optional
        command to send only to the OIII units. (Default: None)
    ha_off_command: str, optional
        command to send only to the offband units of Halpha. (Default: None)
    oiii_off_command: str, optional
        command to send only to the offband units of OIII. (Default: None)
    OH_command: str, optional
        command to send only to the OH skyline monitoring units. (Default: None)
    OH_off_command: str, optional
        command to send only to the OH skyline off band units. (Default: None)
    all_flathaving_command: str, optional
        command to send to all units with a flip flat attached. (Default: None)
    verbose: bool, default: True
        print out info along the way. (Default: True)
    wait_for_response: bool, default: True
        wait for all machines to send a response before returning (until timeout). (Default: True)
    timeout_global: int, default: 120
        time in seconds to wait while pending machines finish tasks before exiting. (Default: 120)
    timeout_seconds: int, default: 10
        time in seconds after which to close the connection and mark a machine as failed. (Default: 10)
    dryrun: bool, default: False
        don't execute the command, but show what commands will be sent to which IP addresses. (Default: False)

    Returns
    -------
    result_df or WebRequestSummary: pandas.DataFrame
        dataframe (or wrapped version) containing the webrequest results.

    """
    if hardware_config_file is not None:
        df = get_status_df(hardware_config_file)
    else:
        df = get_status_df()

    command_dict = {}
    # Parse selection
    # If initial command is given, figure out where to send it
    if command is not None:
        if which not in ["all", "science", "science offs", "OH", "halpha", "oiii"]:
            raise AssertionError(
                "unit selection not recognized. Must select from: 'all','science','science offs','OH','halpha','oiii'"
            )
        if which == "all":
            for ind in df.index:
                unit = df.loc[ind, "Name"]
                ip = df.loc[ind, "IP"]
                name = ind
                command_dict[name] = {"Name": unit, "ip": ip, "command": command}
        elif which == "science":
            mini = df.loc[((df["Filter"] == "ha6647") | (df["Filter"] == "oiii5071"))]
            for ind in mini.index:
                unit = df.loc[ind, "Name"]
                name = ind
                ip = mini.loc[ind, "IP"]
                command_dict[name] = {"Name": unit, "ip": ip, "command": command}
        elif which == "science offs":
            mini = df.loc[
                (
                    (df["Filter"] == "ha_left")
                    | (df["Filter"] == "ha_right")
                    | (df["Filter"] == "oiii_left")
                    | (df["Filter"] == "oiii_right")
                )
            ]
            for ind in mini.index:
                unit = df.loc[ind, "Name"]
                name = ind
                ip = mini.loc[ind, "IP"]
                command_dict[name] = {"Name": unit, "ip": ip, "command": command}
        elif which == "OH":
            mini = df.loc[((df["Filter"] == "OH_off") | (df["Filter"] == "OH"))]
            for ind in mini.index:
                unit = df.loc[ind, "Name"]
                name = ind
                ip = mini.loc[ind, "IP"]
                command_dict[name] = {"Name": unit, "ip": ip, "command": command}
        elif which == "halpha":
            mini = df.loc[df["Filter"] == "ha6647"]
            for ind in mini.index:
                unit = df.loc[ind, "Name"]
                name = ind
                ip = mini.loc[ind, "IP"]
                command_dict[name] = {"Name": unit, "ip": ip, "command": command}
        elif which == "oiii":
            mini = df.loc[df["Filter"] == "oiii5071"]
            for ind in mini.index:
                unit = df.loc[ind, "Name"]
                name = ind
                ip = mini.loc[ind, "IP"]
                command_dict[name] = {"Name": unit, "ip": ip, "command": command}

    if all_flathaving_command is not None:
        mini = df.loc[
            (
                (df["Filter"] == "ha6647")
                | (df["Filter"] == "OH")
                | (df["Filter"] == "OH_off")
                | (df["Filter"] == "oiii5071")
            )
        ]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {
                "Name": unit,
                "ip": ip,
                "command": all_flathaving_command,
            }

    # Now go through and overwrite any specifically asked for ones
    if ha_command is not None:
        mini = df.loc[(df["Filter"] == "ha6647")]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {"Name": unit, "ip": ip, "command": ha_command}
    if oiii_command is not None:
        mini = df.loc[(df["Filter"] == "oiii5071")]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {"Name": unit, "ip": ip, "command": oiii_command}
    if ha_off_command is not None:
        mini = df.loc[((df["Filter"] == "ha_left") | (df["Filter"] == "ha_right"))]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {"Name": unit, "ip": ip, "command": ha_off_command}
    if oiii_off_command is not None:
        mini = df.loc[((df["Filter"] == "oiii_left") | (df["Filter"] == "oiii_right"))]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {"Name": unit, "ip": ip, "command": oiii_off_command}
    if OH_command is not None:
        mini = df.loc[(df["Filter"] == "OH")]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {"Name": unit, "ip": ip, "command": OH_command}
    if OH_off_command is not None:
        mini = df.loc[(df["Filter"] == "OH_off")]
        for ind in mini.index:
            unit = df.loc[ind, "Name"]
            name = ind
            ip = mini.loc[ind, "IP"]
            command_dict[name] = {"Name": unit, "ip": ip, "command": OH_off_command}

    webrequest_df = pd.DataFrame.from_dict(command_dict, orient="index")
    webrequest_df.sort_values(by="ip", inplace=True)
    webrequest_df = webrequest_df[~webrequest_df.Name.isin(skip)]
    webrequest_df = webrequest_df.reset_index(drop=True)

    if (verbose) or (dryrun):
        print("The following commands are queued to send to the following units")
        print("----------------------------------------------------------------")
        print(webrequest_df)
    if dryrun:
        return webrequest_df
    elif not dryrun:
        if verbose:
            print("Sending Request...")
        responses = []
        fulltext = []
        for ind in webrequest_df.index:
            response = SendCommand(
                webrequest_df.loc[ind, "command"],
                ip=webrequest_df.loc[ind, "ip"],
                name=ind,
                timeout_seconds=timeout_seconds,
            )

            if response[1] not in [0, 1, 2]:
                response_dict = json.loads(response[1])
                res = APIResponse(response_dict)
                add_res = "PENDING"
                responses.append(add_res)
                fulltext.append(res)
            elif response[1] == 0:
                responses.append("Command Not Recognized (HTTP err)")
                fulltext.append(response[1])
            elif response[1] == 1:
                responses.append("Machine Down (URL err)")
                fulltext.append(response[1])
            elif response[1] == 2:
                responses.append("Unknown Error")
                fulltext.append(response[1])
        webrequest_df["response_summary"] = responses
        webrequest_df["full_response"] = fulltext
        if verbose:
            print("\n")
            print("Initial Responses:")
            print("------------------")
            print(webrequest_df)
        nPending = webrequest_df.loc[
            webrequest_df.response_summary == "PENDING", "response_summary"
        ].count()
        if verbose:
            print(f"nPending: {nPending}")
        if not wait_for_response:
            return WebRequestSummary(webrequest_df)
        elif nPending == 0:
            return WebRequestSummary(webrequest_df)
        elif nPending > 0:
            start_time = datetime.now()

            if "request_type" in kwargs.keys():
                if kwargs["request_type"] == "exposure":
                    pbar_time = timeout_global - kwargs["readout_time"]
                    print(
                        f"Exposing for {pbar_time} sec, then waiting up {kwargs['readout_time']} s for readout."
                    )
                with tqdm(total=pbar_time) as pbar:
                    while nPending > 0:
                        time.sleep(0.5)
                        pbar.update(0.5)
                        pending_df = webrequest_df.loc[
                            (webrequest_df.response_summary == "PENDING")
                        ]
                        for ind in pending_df.index:
                            response = SendCommand(
                                command="status",
                                ip=pending_df.loc[ind, "ip"],
                                timeout_seconds=timeout_seconds,
                            )
                            if response[1] in [0, 1, 2]:
                                print("pending machine went offline!")
                                webrequest_df.loc[
                                    ind, "response_summary"
                                ] = "Machine Down"
                                nPending -= 1

                            else:
                                response_dict = json.loads(response[1])
                                response_res = APIResponse(response_dict)
                                if response_res.Activity.Any == False:
                                    nPending -= 1
                                    webrequest_df.loc[
                                        ind, "response_summary"
                                    ] = "SUCCESS"
                                    webrequest_df.loc[
                                        ind, "full_response"
                                    ] = response_res

                            time_delta = datetime.now() - start_time
                            if time_delta.total_seconds() >= timeout_global:
                                print("Time Limit Exceeded waiting.")
                                return WebRequestSummary(webrequest_df)
            else:
                while nPending > 0:
                    time.sleep(0.5)
                    pending_df = webrequest_df.loc[
                        (webrequest_df.response_summary == "PENDING")
                    ]
                    for ind in pending_df.index:
                        response = SendCommand(
                            command="status",
                            ip=pending_df.loc[ind, "ip"],
                            timeout_seconds=timeout_seconds,
                        )
                        if response[1] in [0, 1, 2]:
                            print("pending machine went offline!")
                            webrequest_df.loc[ind, "response_summary"] = "Machine Down"
                            nPending -= 1
                        else:
                            response_dict = json.loads(response[1])
                            response_res = APIResponse(response_dict)
                            if response_res.Activity.Any == False:
                                nPending -= 1
                                webrequest_df.loc[ind, "response_summary"] = "SUCCESS"
                                webrequest_df.loc[ind, "full_response"] = response_res

                    time_delta = datetime.now() - start_time
                    if time_delta.total_seconds() >= timeout_global:
                        print("Time Limit Exceeded waiting.")
                        return WebRequestSummary(webrequest_df)

            return WebRequestSummary(webrequest_df)
        else:
            return WebRequestSummary(webrequest_df)
    else:
        return WebRequestSummary(webrequest_df)


class WebRequestSummary:
    def __init__(self, webrequest_df: pd.DataFrame):
        """
        Class container for the responses of a webrequest sent to the pis.

        Parameters
        ----------
        webrequest_df: pandas.DataFrame
        """
        self.df = webrequest_df
        for i in self.df.Name:
            setattr(self, i, self.df.loc[self.df.Name == i, "full_response"].values[0])

    def get_response_by_ip(self, ip: str):
        """
        Obtain the APIResponse object for a given unit

        Parameters
        ----------
        ip: str
            IP address of the unit
        """
        return self.df.loc[self.df.ip == ip, "full_response"].values[0]

    def get_response_by_name(self, name: str):
        """
        Obtain the APIResponse object for a given unit

        Parameters
        ----------
        ip: str
            IP address of the unit
        """
        return self.df.loc[self.df.Name == name, "full_response"].values[0]

    def __str__(self):
        return self.df.__str__()

    def __repr__(self):
        return self.df.__repr__()


class APIResponse:
    def __init__(self, response_dict):
        """
        Container for webserver response.
        Use APIResponse.info() to see fields.

        Parameters
        ----------
        response_dict: dict
            dictionary of the API response from the webserver
        """
        self.response_dict = response_dict
        self.result = self.response_dict["Result"]
        self.IP = self.response_dict["IPAddress"]
        self.response_fields = self.construct_dataframes()

    def __repr__(self):
        return f"APIResponse[{self.IP}]"

    def __str__(self):
        return f"APIResponse[{self.IP}]"

    def info(self, verbose=False):
        """
        Prints the accessible fields (attributes) of the object.

        Parameters
        ----------
        verbose: bool, default: False
            show just the field names, or also all the values
        """
        if verbose:
            print(f"Status Response for Unit at IP: {self.IP}")
            for i in self.response_fields:
                print("\n \n")
                print(f"ATTRIBUTE: {i}")
                print(getattr(self, i))
        else:
            print(
                f"Status Response for Unit at IP: {self.IP} \n Accessible Fields: \n {self.response_fields}"
            )

    def construct_dataframes(self):
        """
        Constructs individual DataFrames for each main field in the status response, and wrap them.
        """
        response_fields = []
        for i in self.response_dict.keys():
            if i not in ["Result", "IPAddress"]:
                setattr(
                    self,
                    i,
                    WrapDF(
                        pd.DataFrame.from_dict(self.response_dict[i], orient="index")
                    ),
                )
                response_fields.append(i)
        return response_fields


def ParseResponse(response, return_type="dict"):
    """
    Parses the byte-string response from the webserver into either a dictionary or an API object.

    Parameters
    ----------
    response: byte
        response from the webserver (generally a status)
    return type: str, default: 'dict'
        type of object to return. Options are 'dict' or 'API'.
    """
    parsed_response = json.loads(response.decode("utf-8"))
    if return_type == "dict":
        return parsed_response
    elif return_type == "API":
        return APIResponse(parsed_response)
    else:
        raise AssertionError("Return type must be either dict or API")


class WrapDF:
    """
    Dataframe wrapper that provides a 'get' method.
    """

    def __init__(self, df):
        """
        Parameters
        ----------
        df: pandas.DataFrame

        """
        self.df = df
        for i in self.df.index:
            setattr(self, i, self.df.loc[i].values[0])
        self.logstring = self.df.to_string()

    def __repr__(self):
        return self.df.__repr__()

    def __str__(self):
        return self.df.__str__()

    def get(self, field):
        """
        Get the value of an associated field. Wrapper for a loc type command.

        Parameters
        ----------
        field: str
            name of the field to get value for.
        """
        return self.df.loc[field].values[0]
