#!/usr/bin/env python
# coding: utf-8

# # QuickObserve
# 
# While `AutoObserve` will be the primary driver of nightly observations, it may be useful to be able to manually set up and run a night's worth of observing explictly (that is, no observing plans, simply write out in a script what you want the telescope to do). This is a similar method to how the old Narrowband `.sh` scripts worked. 
# 
# Similar functionality is provided by the `QuickObserve` class. The class is responsible for setting up a target and carrying out observations of it... and nothing more. That means it will slew to the target, set the tilts, start guiding, expose, stop guiding, and exit. Meanwhile, other things you may want (and need) to do should be done in a standalone script surrounding `observe` calls of a `QuickObserve` object. 
# 
# Let's see how this looks in practice. Below is an example of a "full night" script, in which we establish two `QuickObserve` targets: M82, and some standard star. The needed primatives (direct control utility functions) are called to ensure everything surrounding the observation is as needed. And in this case, we do a flatfield run. 

# In[ ]:


# Imports
from dfobserve.observing import QuickObserve 
from dfobserve.utils.CameraUtils import (AllSetCameraTemperatures, 
                                         AllFlatFieldExposure,
                                         AllDarkExposure)
from dfobserve.utils.FlipFlatUtils import (AllCloseFlipFlats, 
                                           AllOpenFlipFlats, 
                                           AllTurnOffFlipFlaps, 
                                           AllTurnOnFlipFlaps) 
from dfobserve.utils.MountUtils import StartMount, StopMount, ParkMount
import time


# In[ ]:


# QuickObserve Object Setups
m82 = QuickObserve('M82',
                    ha_tilt=12.5,
                    oiii_tilt=12.0,
                    exptime=3600,
                    offband_exptime=600,
                    niter=1,
                    )


some_standard = QuickObserve('GD 153',
                            ha_tilt=12.5,
                            oiii_tilt=12.0,
                            exptime=60,
                            offband_exptime=5,
                            niter=2)


# In[ ]:


# Line By Line Execution 
AllSetCameraTemperatures(-30)
time.sleep(30)
# You could check camera temps here 
AllOpenFlipFlats() 
StartMount()
# Observe() handles slewing to target, guiding, tilting, dithering, 
# and taking niter sci exposures (with offs throughout) (then dithers back)
m82.observe(dither_east=15,dither_north=15) 
m82.observe(dither_east=-15,dither_north=-15)

# This block takes some flats
AllCloseFlipFlats()
AllTurnOnFlipFlaps() 
AllFlatFieldExposure(exptime=5,n=3) #which=science by default so just those with flipflats
AllTurnOffFlipFlaps() 
AllOpenFlipFlats() 

some_standard.observe() # Now slew to standard and do stuff 

AllCloseFlipFlats()
ParkMount() 
StopMount() 
AllDarkExposure(3600)
AllSetCameraTemperatures(20)

