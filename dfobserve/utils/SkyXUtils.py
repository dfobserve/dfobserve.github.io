import subprocess as sp
from ..exceptions import *

__all__ = ["check_target_exists"]


def check_target_exists(target_name: str, host: str = "127.0.0.1"):
    """
    Check whether a target name is recognized by TheSkyX.
    This function constructs a js query which is saved to a temporary
    file that is then sent to TheSkyX via the `skysend` command.

    Parameters
    ----------
    target_name: str
        name to check in the database.
    host: str, default: '127.0.0.1'
        IP address associated with TheSkyX server

    Returns
    -------
    found: bool
        If the target is found, returns true, else false. If another response occurs,
        an error is thrown.
    """
    query1 = f"""
/* Java Script */

var Target = '{target_name}';
var Out="";
var err;
sky6StarChart.LASTCOMERROR=0;
sky6StarChart.Find(Target);
err = sky6StarChart.LASTCOMERROR;
if (err!=0)"""
    query2 = """
{
Out = "NotFound";
}
else
{
    Out = "Found";
}
        """
    query = query1 + query2
    fn = "tmp.js"
    with open(fn, "w") as f:
        f.write(query)
    command = f"skysend {host} {fn}"
    r = sp.run(command, shell=True, capture_output=True, encoding="utf-8")
    s = r.stdout
    s = s.split("|")[0]
    if s == "Found":
        return
    elif s == "NotFound":
        raise TargetNotFoundError("Target not in TheSkyX Databasex")
    else:
        raise UnknownCommunicationError("Error Communicating with SkyX")


def StartAutoGuide():
    command = "ncommand -l 'foo=new TSXAutoGuider(); foo.magic()'"
    r = sp.run(command, shell=True, capture_output=True)
    return r


def StopAutoGuide():
    command = "ncommand -l 'foo=new TSXAutoGuider(); foo.stop()'"
    r = sp.run(command, shell=True, capture_output=True)
    return r


def GetMountPointing(host: str = "127.0.0.1"):
    """
    Retrieve the position of the mount (RA,DEC,ALT,AZ,HA)
    """
    query = """
/* Java Script */
var Out;
var dRA;
var dDec;
var dAz;
var dAlt;
var coordsString1;
var coordsString2;
sky6RASCOMTele.Connect();
if (sky6RASCOMTele.IsConnected==0) {
    Out = "Not connected"
} else {
    sky6RASCOMTele.GetRaDec();
    dRA = sky6RASCOMTele.dRa;
    dDec = sky6RASCOMTele.dDec;
    sky6Utils.ComputeHourAngle(dRA);
    dHA = sky6Utils.dOut0;
    sky6Utils.ConvertEquatorialToString(dRA,dDec,5);
    coordsString1 = sky6Utils.strOut;
    sky6RASCOMTele.GetAzAlt();
    Out = coordsString1;
    Out += " Alt: " + parseFloat(Math.round(sky6RASCOMTele.dAlt*100)/100).toFixed(4);
    Out += " Az: " + parseFloat(Math.round(sky6RASCOMTele.dAz*100)/100).toFixed(4);
    Out += " HA: " + parseFloat(Math.round(dHA*10000)/10000).toFixed(4);
};
"""
    fn = "tmp.js"
    with open(fn, "w") as f:
        f.write(query)
    command = f"skysend {host} {fn}"
    r = sp.run(command, shell=True, capture_output=True)
    s = r.stdout.decode("latin-1")
    response = s.split("|")[0]
    comment = s.split("|")[1]
    if comment.startswith("No error."):
        splits = response.split()
        ra = splits[1][:-1] + ":" + splits[2][:-1] + ":" + splits[3][:-1]
        dec = splits[5][1:-1] + ":" + splits[6][:-1] + ":" + splits[7][:-1]
        alt = splits[9]
        az = splits[11]
        ha = splits[-1]
        out_dict = {"ra": ra, "dec": dec, "altitude": alt, "azimuth": az}
        return out_dict
    else:
        raise UnknownCommunicationError("Error Communicating with SkyX")
