#!/usr/bin/env python
# coding: utf-8

# # The AutoObserve Class
# 
# Now that we have `Observation`s ready to go, we can move on to setting up an `AutoObserve` (which can happen in the same script, below target creation. To remind ourselves, here's all the code to setup the `m82` Observation from before:

# In[1]:


from dfobserve.observing import Observation
m82 = Observation(target='M82',
                  exptime=3600,
                  iterations=2,
                  do_focus=True,
                  min_altitude=35)
m82.configure_observation(wait_until='target_rise',
                    dither_angle=15, # dither angle from target center
                    dither_pattern=[5,3,7,1,9,2,8,4,6], # dither pattern on grid
                    randomize_dithers=True, #choose random dither pattern
                    off_band_exptime=600, # 20 sec exposures for the off bands
                    off_band_throughout=True)
m82.configure_calibrations(n_darks=1,
                            dark_exptime=60,
                            take_darks='after',
                            n_flats=1,
                            flat_exptime=60,
                            take_flats='all')
m82.configure_standards(use='nearest',
                        n_standards=1,
                        when='all')
m82.set_tilts('halpha',14.5)
m82.set_tilts('oiii',12.6)


# Now, let's get going with `AutoObserve`:

# In[2]:


from dfobserve.observing import AutoObserve

targetlist = [m82]


# For now, we only have 1 target, but at this stage, we'd normally compile our targets (`Observation` objects) into a list as shown. We'll now feed this into `AutoObserve`:

# In[3]:


obs = AutoObserve(targetlist,
                  guide=True,
                  save_log_to='./',
                  data_dir_on_pis=None)


# In the bit above, we get a note that the logfile will be saved in the current directory (since we asked), with the date. We also get some errors trying to mount the pis on the control pc.... because I'm running this at home, not on the control pc. Let's not worry about that! 
# 
# With this set up, all we need to do is run

# In[ ]:


obs.observe()


# And we're off to the races! I obviously won't run that here at home. This bit will first iterate over the target list, obtain each target's observing plan, and then execute it. It also handles all needed slewing, checking if the dome is open, starting tracking/guiding, tilting the filters for each target, all that good stuff. 
# 
# Right now, it is in a "dumb" state of not having bailouts for things like sunrise, but I'll be adding those things in very shortly.
# 
# ### Conclusion 
# 
# That's it for this! But there's a few more major pieces of the code base that are worth knowing about, and we'll discuss that next. 
