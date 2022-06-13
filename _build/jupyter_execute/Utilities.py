#!/usr/bin/env python
# coding: utf-8

# # Utilities 
# 
# The following indicates some of the base-level utilities present in the package, which can be used interactively in a "line by line" observing style. This is particularly useful for testing. 
# 
# As a note, the `DFObserve` package directory (i.e., the outermost directory) contains a file called `interactive_startup.py`. This file contains a bunch of imports to get all the organized utility functions into your interactive Python session in one go, defines a few helper functions, etc. I recommend running this Python file when running interactively. 
# 
# The utilities are all stored in the `dfobserve.utils` submodule, and are organized by the following: Cameras, Filter Tilters, FlipFlats, Hardware, Mount, Network, NMS (New Mexico Skies), and The Sky X. 
# 
# ## Camera Utils 
# 
# One of the most useful set of utils for testing, these allow you to take exposures through the webserver. 
# 
# - `AllExpose`: Take an exposure. Supply `exptime`, `which` (to send command to, as recognized by `SendWebRequestNB`), a dictionary of any extras (like `savedir`), and any `**kwargs` recognized by `SendWebRequestNB`. A useful one is `skip`, which lets you skip sending the command to a list of units. 
# - `AllScienceExposure`: Take an exposure in which the ons (narrowband units) take an exposure while the offs take shorter, multiple exposures during. 
# - `AllFlatFieldExposure`: Take a flat on all units (or well, whichever specified by `which`). Relies on you having closed and turned on the flip flats first. 
# - `AllDarkExposure`: Similar but for darks. 
# - `Autofocus`: This runs the focus-run script (by Jeff). Has a bunch of params. 
# - `AllSetCameraTemperatures`: set the camera temps. If you pick a number > 15, it disables the coolers. 
# - `AllCheckCameraTemperatures`: Check that the camera temps are within tolerence of some desired value. 
# 
# A typical "quick" exposure command sent to all units might look like:

# In[ ]:


r = AllExpose(exptime=300,
              extras={'savedir':'/data/2022-10-24'},
              skip=['Dragonfly302']) 


# Because this is an expose type command, a progress bar will fill up with the asked for exposure time, then idle till readout is complete (usually takes a few seconds). 
# 
# If you want to test by sending an expose command to only a few units (i.e., it's easier to describe which to send to than which to skip), there's a `calc_skips()` function in the `interactive_startup.py` that works as:

# In[ ]:


skips = calc_skips(use=['Dragonfly309','Dragonfly310'])


# In the above example, you'd get a skip list of everything but those two units, which you can feed to `AllExpose`. 
# 
# As a reminder, the `which` param on all these expose commands goes to `SendWebRequestNB` which has convenience options like "all", "science", "science offs", "OH", "halpha" and "oiii". 

# ## Filter Tilter Utils 
# 
# The filter tilter utils are fairly self explanatory. We have 
# 
# - `AllTiltScienceFilters`: Tilt the science filters. Args are `ha_tilt=_` and `oiii_tilt=_`, along with any `**kwargs` recognized by `SendWebRequestNB`. Only the filters marked science will be tilted. 
# - `AllMoveFilters`: Move the science filters by a certain amount. Args are `ha_move` and `oiii_move`. 
# - `AllGetFilterTilts`: Get the filter tilts of the science filters. Returns a df showing the Name, Filter, Angle, RawAngle, and ZeropointAngle. 
# - `AllCheckFilterTilts`: Check that the filter tilts are within tolerance of some desired tilt. I.e., after running `AllTiltScienceFilters` to 10 and 15 degrees, plug 10 and 15 into this function and get a df output that shows whether the filters are in tolerence of this. 

# **Note:** Don't confuse `AllCheckFilterTilts`, which checks the success of a single tilt attempt, with `AllCheckFilterTilters`, a toplevel function part of the `checks` submodule that gets run during `AllCheckDragonfly` or which can be used to mark units down if tilts are out of tolerance across a set of tilt checks. 

# ## Flip Flat Utils
# 
# These are even easier. 
# 
# - `AllOpenFlipFlats`: Open them. 
# - `AllCloseFlipFlats`: Close them. 
# - `AllTurnOnFlipFlats`: Turn them on -- arg `lampbrightness` controls the brightness, default is 60. 
# - `AllTurnOffFlipFlats`: Turn them off. 
# 
# 
# All of these take the `which` param recognized by `SendWebRequestNB` along with the manual `skip` param to skip individual units. 

# ## Hardware Utils 
# 
# The Hardware Utils is basically a single class, `HardwareStatus`, whose job is to manipulate the hardware status file that has units marked up and down for use during observing. The current file running this is `"/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_CURRENT_STATUS.csv"`. 
# 
# **Note**: There is CLI support for this util. See `Command Line Interface`. 
# 
# The basic usage looks like the following examples:

# In[ ]:


hs = HardwareStatus()


# In[ ]:


hs.InitializeHardwareStatus()


# The above sets all the units to `'UNDETERMINED'`. 

# In[ ]:


hs.MarkUnitDown('Dragonfly310') 


# Mark the Dragonfly310 unit as DOWN. 

# In[ ]:


hs.MarkUnitUp('Dragonfly301')


# Mark the Dragonfly301 unit as UP. 

# In[ ]:


hs.MarkAccessibleUnitsUp() 


# Ping the webserver with a `status` command and mark any units that connect and send a response as UP. 

# In[ ]:


hs.MarkAllUnitsUp() 
hs.MarkAllUnitsDown() 


# As expected, these mark all units as up or down. 

# In[ ]:


hs.get_status(which='all') 


# This returns the contents of the csv file, which is the name of each unit and whether it is up or down. When `verbose` is `True`, prints to the terminal. If `return_units` is `True`, returns the status response dataframe. 

# In[ ]:


hs.get_status(which='up')
# or 
hs.get_status(which='down')


# These return simple lists of which units are marked up or down, e.g., `['Dragonfly301','Dragonfly302',...]`. Useful for quickly grabbing a list to `skip` sending commands to. 

# In[ ]:


hs.get_status(which='viz')


# This last handy thing prints a visual map of the layout of the units, and colors them green if up and red if down. 

# ## Mount Utils 
# 
# Utilities for controlling the mount. At this point *most* are just wrappers for Bob's code. 
# 
# - `DitherMount`: Dither the mount. Takes two values, `east=_` and `north=_`, floats in arcmin. Will dither by that amount. 
# - `GuideMount`: Runs `guider magic`. 
# - `HomeMount`: Homes the mount
# - `StartMount`: Starts tracking
# - `StopMount`: Stops Tracking 
# - `ParkMount`: Parks Mount 
# - `SlewMount`: Slew the mount to a target (target must be in the SkyX Database). 

# ## Network Utils 
# 
# Grab a dataframe with the unit names, IP addresses, which filter is on them, and some other ancillary info by calling

# In[ ]:


sdf = get_status_df() 


# ## NMS Utils 
# 
# Grab info about what's going on in NMS. (Under Construction). 
# 
# - `isRoofOpen`: Returns true if the dome is open, false if not. 

# ## SkyX Utils 
# 
# Wrappers for JS calls to the SkyX. 
# 
# - `check_target_exists`: Add a target name and see whether it exists in the skyX database. Raises a `TargetNotFound` Error if not. 
# - `GetMountPointing`: Return parsed dictionary containing the ra, dec, alt, and az of the telescope as returned by the mount. Used for passing into the expose commands for being saved in a header. 
