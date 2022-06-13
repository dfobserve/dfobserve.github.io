#!/usr/bin/env python
# coding: utf-8

# # The Observation Class
# 
# These two classes work in concert to setup and run observations on the telescope at a high level. They have many defaults set but allow for a lot of flexibility as well. 
# 
# Below, we'll set up a standard "observing script" or configuration, which will tell the codebase how to carry out observations. 
# 
# ## Observation
# 
# The `Observation` class is responsible for setting up individual targets and the "way" in which we want to observe them. Let's import it:

# In[1]:


from dfobserve.observing import Observation


# ### Instantiation 
# The first thing we need to do is instantiate an `Observation` object. This can be done with a few simple keywords:

# In[2]:


m82 = Observation(target='M82',
                  exptime=3600,
                  iterations=2,
                  do_focus=True,
                  min_altitude=35)


# We've now set up `m82` as a target. 
# 
# - The `target` keyword specifies a name. For now, this *must* be a name recognized by TheSkyX. You can confirm this by running the `check_target()` method so long as you are on the machine with TheSkyX installed.
# - The `exptime` keyword sets the primary exposure time (that is, for the science filters on the target). 
# - The `iterations` keyword sets the number of science exposures to take in total on this target 
# - `do_focus` indicates that we want to do focus runs before starting observations of this target
# - `min_altitude` sets a mininum altitude to observe the target at. If it is below this altitude at the start of a proposed observation, it won't exposure and will move on.
# 
# ### Observing Configurations
# 
# Now that we have the basics, we can add some more specific configurations to our observations:

# In[3]:


m82.configure_observation(wait_until='target_rise',
                    dither_angle=15, # dither angle from target center
                    dither_pattern=[5,3,7,1,9,2,8,4,6], # dither pattern on grid
                    randomize_dithers=True, #choose random dither pattern
                    off_band_exptime=600, # 20 sec exposures for the off bands
                    off_band_throughout=True)


# Here, we use the `configure_observations()` method to set a few more parameters. 
# 
# - `wait_until` sets when the code will idle until before starting up observations. Options include `'sunset'`, `'moonset'`, `'target_rise'` or a manual time, in the format `'HH:MM:SS'`. That time is assumed to be local, but if you enter something that ends in UTC, e.g., `'HH:MM:SSUTC'`, it will convert to UTC. Note that this is only really important for the first target in a targetlist, as the others should execute as soon as the first target finishes. 
# - `dither_angle` sets the amount the telescope will dither between exposures (in arcminutes)
# - `dither pattern` tells it which pointings in a 3x3 grid dither pattern to observe. The pattern looks like 
# 
# 
# |   |   |  |
# |--- | --- | --- |
# | 1  |  2  |  3 |
# | 4  |  5  |  6 |
# | 7  |  8  |  9 |
# 
# - `randomize_dithers` will shuffle the dither pattern used, so that different pointings are (hopefully) obtained over time. 
# - `off_band_exptime` sets how long the medium band filters should expose. This is usually set to something shorter than the primary exptime to avoid saturation.
# - `off_band_throught` is a flag which tells the code to take as many exposures of length `off_band_exptime` during each science exposure. Otherwise only 1 will be taken.
# 

# ### Calibration Configurations
# 
# Next, lets configure the basic calibrations (darks and flats):

# In[4]:


m82.configure_calibrations(n_darks=1,
                            dark_exptime=3600,
                            take_darks='after',
                            n_flats=1,
                            flat_exptime=60,
                            take_flats='all')


# These are pretty self explanatory. We decide how many darks and flats to take (and what the exposure time for each should be). We also decide *when* we want to take each. Options include 'before', 'between', 'after', and 'all'. If we select before or after, that calibration frame will only be taken before, or after, all the science/offband exposures. If we select between, we'll get them in between iterations, and if we select all, we'll get them before, between, and after. We can add more options here later (like 'before-after'). 
# 
# The above configuration witll take flats (1) between every science iteration, as well as before and after the target is observed, while the darks will only happen at the end for this object. 
# 
# ### Standards Configuration 
# 
# We can now setup how we want standards (like standard stars) to be observed.

# In[5]:


m82.configure_standards(use='nearest',
                        exptime=30,
                        n_standards=1,
                        when='all')


# The code (will) maintain a list of accessible standards; here we select `use='nearest'` to just go to the nearest one to the target. We set the number of standards to take, and when to take them (here, we'll have it before, between iterations, and after the target is observed). 
# 
# ### Setting Tilts
# We can easily set the tilts for the target:

# In[6]:


m82.set_tilts('halpha',14.5)
m82.set_tilts('oiii',12.6)


# (this function takes many iterations of those strings, like 'Halpha' and 'o3'). 
# 
# As a reminder, you can turn velocities to tilts using the handy online calculator.

# ## Constructing an Observing Plan 
# 
# All of the above methods simply serve as data entry. To combine it all together into a formal plan (along with checking various components to be sure things look good), we need to run `construct_observing_plan()`.
# 

# In[7]:


m82.construct_observing_plan()


# The output of this is the internal that controls what order the code will go through when taking exposures. We can also view the plan in a more friendly way (see below). But let's first show some ways in which `construct_observing_plan()` can error out if there are issues with the observing plan. 
# 
# On the date of this writing (2022-05-05), The system NGC 5846 rises above the typical minimum altitude of 35 degrees at around 10 pm. Let's see what happens if we add this object, and try to observe it with a `wait_until` of sunset.

# In[8]:


ngc = Observation(target='NGC 5846',
                  exptime=3600,
                  iterations=2,
                  do_focus=True,
                  min_altitude=35)
ngc.configure_observation(wait_until='sunset',
                    dither_angle=15, # dither angle from target center
                    dither_pattern=[5,3,7,1,9,2,8,4,6], # dither pattern on grid
                    randomize_dithers=True, #choose random dither pattern
                    off_band_exptime=600, # 20 sec exposures for the off bands
                    off_band_throughout=True)
ngc.construct_observing_plan()


# As we can see, the code returns a `TargetNotUpError`, warning you that you attempted to start observing at sunset, but the target is not up at this time. For now, if you want to start at sunset anyway because you are planning to take flats, etc., at sunset which will take you till the target rises, you can lower the `min_altitude` accordingly. You could also use `QuickObserve` instead. 
# 
# The code should return valuable errors for all sorts of target issues, such as the target rising too late in the night, or the moon setting too late to be useful, if you're waiting until moonset, or your observing plan has more exposure time than the target is up for. 
# 
# As a note, these calculations are carried out via `astropy`, and you can see some of them in action if you wish. For example, 

# In[12]:


from dfobserve.observing import get_sunset, get_sunrise, get_moonset

print(get_sunset())
print(get_sunset())
print(get_moonset())


# And you can set specific dates if you choose:

# In[14]:


print(get_sunset('2022-05-15'))


# The `Observation` objects can also calculate the target's rise and set time on a given night:

# In[17]:


print(m82.calc_target_rise())
print(m82.calc_target_set())


# As we can see, M82's rise time is shown to be 19:47 (which is just after sunset). If it were before sunset, the rise time would be marked as sunset. And it sets at 01:13 AM. This function can output either local time or UTC by setting a flag:

# In[18]:


print(m82.calc_target_rise(return_local=False))


# As a note, this is all currently working because target names conform to names recognizable by `astropy.coordinates.SkyCoord`. However, we can easily allow arbitrary targets (with arbritrary coordinates) to be added, and all of this will still work. 

# ### Viewing Observing Plans 
# 
# And that's it! We should now have a servicable observing plan. Let's take a look at what the calculated plan looks like:

# In[19]:


m82.view_observing_plan()


# We can see that at the top, we get some summary information about specifically which dither pointings will be taken and confirm our tilts. 
# 
# Below that, more interestingly, we have a set of proposed observations. This will be the plan followed by `AutoObserve` later, so it's nice to confirm what it's going to attempt to do. We can see that we take standards before, between, and after (due to the `when='all'` key being set), this is also true for flats. We're smart enough to start with flats because the flip flats should already be closed. Darks, meanwhile, are only taken at the end of the run for this target (as desired). 
# 
# We can also see that the code has calculated, for a chosen off-band exposure time of 600 seconds, how many we can fit into one 3600 science exposure (4). At the moment, I think I subtract 1-2 to account for readout overheads; this can be adjusted. 
# 
# At the bottom, we get some info about how long we'll be on this target (not counting overheads) as well as how many exposures we expect (not including any focus stuff). 
# 
# ### Conclusion 
# 
# This object should now be ready to go. We can set up any number of targets in the same way, and feed them into `AutoObserve` as a targetlist. Let's try that next.
