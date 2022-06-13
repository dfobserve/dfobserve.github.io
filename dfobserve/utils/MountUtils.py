"""
Utility functions for controlling the mount.
"""

import subprocess as sp

send_web_request = "python3 C:/Dragonfly/Programs/SendWebRequestToArray.py"
# Not needed here because the mount will be directly accessible
# from the mount pc


def DitherMount(east, north):
    """
    Dither the mount in a certain direction
    """
    # In arcmin -- do any needed transformations here

    east_command = f"mount dither {east} E"
    north_command = f"mount dither {north} N"
    if east != 0:
        r = sp.run(east_command, shell=True, capture_output=True)
    if north != 0:
        r1 = sp.run(north_command, shell=True, capture_output=True)
    string_response = r.stdout.decode("utf-8") + "\n" + r1.stdout.decode("utf-8")
    return string_response


def GuideMount():
    """
    Attempt to start guiding
    """
    comm = f"'guider magic'"  # NEEDS some checks apparently
    res = sp.run(comm, shell=True, capture_output=True)
    return res


def HomeMount():
    """
    Home the Mount
    """
    comm = f"mount home"
    res = sp.run(comm, shell=True, capture_output=True)
    return res


def StartMount():
    """
    Start tracking
    """
    comm = f"mount --nmount 1 start"
    res = sp.run(comm, shell=True, capture_output=True)


def ParkMount():
    """
    Park Mount
    """
    comm = f"mount --nmount 1 park"
    res = sp.run(comm, shell=True, capture_output=True)
    return res


def StopMount():
    """
    Stop mount
    """
    comm = f"mount --nmount 1 stop"
    res = sp.run(comm, shell=True, capture_output=True)
    return res


def SlewMount(target):
    """
    Slew mount to a target

    Parameters
    ----------
    target: str
        target to slew the mount to
    """
    comm = f"mount --nmount 1 goto {target}"
    res = sp.run(comm, shell=True, capture_output=True)
    return res
