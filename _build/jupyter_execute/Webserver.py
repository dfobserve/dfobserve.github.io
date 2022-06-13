#!/usr/bin/env python
# coding: utf-8

# # Communicating through the Webserver 
# 
# At a fundamental level, everything is handled by web requests sent through a web server to some or all of the raspberry pis that control each unit. 
# 
# ## SendCommand
# 
# The basic function for carrying out a command is

# In[1]:


from dfobserve.webserver import SendCommand


# who's simple docs look like this:

# In[ ]:


def SendCommand(command: str,
                ip: str,
                timeout_seconds: int =10,
                name: str = None,
                verbose: bool = False):


# This function takes a url string command that is recognized by the server. This can be simple, like `'status'`, or complex, like `'expose?type=light&time={exptime}&name={name}'`. 
# 
# The function needs the `ip` address to send it to (on the local network), and how long to wait before timing out on no response. One can also add the name of the unit (e.g., "Dragonfly301") for prettier printing; this is done automatically when some other functions run this command. The main `SendWebRequest` below essentially wraps this function (which does some checks on what gets returned), and determines which commands should go to which IP addresses,
# 
# ## SendWebRequestNB
# 
# The big boy of this module is `SendWebRequestNB`, which provides the flexibility to send different commands to all of the different subsystems on the instrument. Its setup looks like this:

# In[ ]:


def SendWebRequestNB(command: str = None,
                    which: str = 'all',
                    ha_command: str = None,
                    oiii_command: str = None,
                    ha_off_command: str = None,
                    oiii_off_command: str = None,
                    OH_command: str = None,
                    OH_off_command: str = None,
                    all_cals_command: str = None,
                    verbose: bool= True,
                    wait_for_response: bool = True,
                    timeout_global: int = 120,
                    timeout_seconds: int = 10,
                    dryrun = False):


# In simpler cases, we have a single command we want to send to all, or a simply-defined subset of the units. For example, we might want to send the `AllCloseFlipFlats()` base (web) command, and we know it should just go to the science units (since the others don't have flip flats). Indeed, the way the `AllCloseFlipFlats` assumes we want just the science frames. So under the hood, it runs 

# In[ ]:


SendWebRequestNB(command='flipflat?command=close&remote=true',
                              which=which,
                              **kwargs)


# where in this case, `which` is going to be set to `'science'`. The currently supported options are 'all', 'science', 'science offs', and 'OH' (which sends to both the OH on and OH off units). 
# 
# Beyond this simple usage, we have optional keyword arguments for every single type of unit we have, separately, as well as one for all the cals together. So if we need to send different commands to h-alpha and oiii, we can do that. 
# 
# Indeed, these special keywords *overwrite* the default command. So we could send a command to 'all' using the primary command, and then just overwrite what gets sent to OIII with a separate command. 
# 
# Finally, we have some flags like verbose (print stuff), whether to try to wait for the sticks to *complete* the command (for up to `timeout_global` seconds), and the timeout in seconds for individual connections to send a response before being marked down with the connexction closing. `dryrun` lets us queue a command and look at what we're going to send to each unit in a table before we actually pull the trigger. 
# 
# The Modules inside the `utils` submodule, e.g., `CameraUtils`, or as we've seen, `FlipFlatUtils`, are basically wrappers around `SendWebRequestNB`, allowing you to queue up somewhat complex commands without actually messing with a lot of options or remembering the string-based url-type commands. But you can always resort to this. 
# 
# For example, you could write a "fully manual" observing script that specifies in serial every command to send using this. You can also easily *add* convenience functions by wrapping this function and deciding on which things it will set up automatically. 
# 
# To give a concrete example, let's look at the bread and butter command: `AllScienceExposure`:

# In[ ]:


def AllScienceExposure(exptime: int,
                    off_exptime: int,
                    n_offs: int,
                    oh_exptime: int=None,
                    name: str = None,
                    ra: float = None,
                    dec: float = None,
                    alt: float = None,
                    az: float = None,
                    wait_readout: int = 60,
                    **kwargs):
    '''
    Execute a standard science exposure
    '''
    command = f"expose?type=light"
    if isinstance(name,str):
        command+=f"&name={name}"
    if isinstance(ra,(float,int)):
        command+=f"&ra={ra}"
    if isinstance(dec,(float,int)):
        command+=f"&dec={dec}"
    if isinstance(alt,(float,int)):
        command+=f"&alt={alt}"
    if isinstance(az,(float,int)):
        command+=f"&az={az}"
    
    science_command = command + f"&time={exptime}"
    offs_command = command + f"&time={off_exptime}&nlight={n_offs}"
    if isinstance(oh_exptime,int):
        oh_command = command + f"&time={oh_exptime}"
    else:
        oh_command = science_command
    timeout = exptime+wait_readout
    response = SendWebRequestNB(command=offs_command,
                                which='science offs',
                                ha_command=science_command,
                                oiii_command=science_command,
                                OH_command=oh_command,
                                OH_off_command=oh_command,
                                timeout_global=timeout,
                                **kwargs)
    return response


# This function is responsible for (in most case) executing the science exposures. It reads in some specific things fed to it by `AutoObserve`, retrieved from an object's observing plan. It allows for the OH-band exptime to be set (but if it isn't, uses the science exposure time). It sets up the string commands for the science and offs, telling the offs to do n iterations (based on other calculations). And at the end, we can see it wraps `SendWebRequestNB`. 
# 
# Ironically, the shortest way was by setting the `offs_command` to the primary, with `which = 'science offs'`, which handles the ha and oiii offbands. Then we feed the science command to both ha and oiii, and the oh_command to both oh and oh off. And we use a special global timeout set to the exposure time plus some number of seconds, to ensure the script waits the length of the exposure plus some read out time, before closing. 
# 
# `SendWebRequestNB` constructs a `pandas` `DataFrame` to store all the commands it is going to send where; this data frame with the responses at the time it finishes (either all sticks respond as 'SUCCESS' or the timeout is reached) is returned and added to the log (or printed for examination). 

# Let's say we want to tilt Halpha filters to 12 degrees. We'd run

# In[ ]:


res = SendWebRequestNB(ha_command='device/filtertilter?command=set&argument=12')


# This would send the request only to the Halpha units. Alternatively, 

# In[ ]:


SendWebRequestNB(command='device/filtertilter?command=set&argument=12',which='science')


# would tilt both the Halpha and OIII filters to this amount, and 

# In[ ]:


SendWebRequestNB(command='device/filtertilter?command=set&argument=12')


# would send it to all units (even the calibration ones).

# In[ ]:




