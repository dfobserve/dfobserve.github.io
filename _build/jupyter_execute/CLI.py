#!/usr/bin/env python
# coding: utf-8

# # Command Line Interface

# Some of the utilities and functions have been set up to allow for command line interface (CLI) usage. This is primarily for testing convenience but not the main purpose of this package. I usually recommend opening ipython and using that, since the rich status objects returned can be interrogated. 
# 
# The primary supported CLI tools at the moment relate to `AllCheckDragonfly`, but some of the others have it as well. CLI is instantiated via the `fire` package by Google. Here's a running list. 
# 
# ## AllCheckDragonfly (and associated)
# 
# All of the afternoon-check tools have CLI enabled. So within python, where you'd run:

# In[ ]:


from dfobserve.checks import AllCheckDragonfly 

r = AllCheckDragonfly() 


# From the terminal, you'd run 

# In[ ]:


dfAllCheckDragonfly


# As a note, the definitions here in the terminals are just aliases in the `~/.bashrc` script. What's actually being run is 

# In[ ]:


python ~/git/DFObserve/dfobserve/checks/check_dragonfly.py 


# After which args are passed and parsed. For example, our standard command-line usage of skipping certain tests looks like:

# In[ ]:


dfAllCheckDragonfly --skip=focusers,mount


# The skippable tests are
# - `mount`, which skips the mount test, 
# - `network`, which skips marking all accessible units up first. Only recommended when running allcheck a second or third time after already marking some units down. 
# - `focusers`, which skips the focuser checks (which involve moving the focusers by N steps and checking tolerance),
# - `cameras`, which skips the camera tests that marks units down if bias testing is out of acceptable bounds
# - `filters`, which skips tilting the filters to certain tilts and checking tolerances (default is 5,0). 
# 
# At the end, a summary with the map of units colored by up/down is showed. 
# 
# Techincally, some of those tests have optional `kwarg_dict={}` arguments allowing you to modify the nature of the checks (say, testing different or more angles on the filter tilters, or the tolerance of the steps in the focuser test). But the goal is to have an well-calibrated nightly set of defaults one doesn't need to change. 
# 
# As mentioned, the submodules of AllCheckDragonfly can be run individually. From the command line, the supported options (currently) are 

# In[ ]:


AllCheckCameras


# and

# In[ ]:


AllCheckFocusers


# ## Hardware Status
# 
# The other main thing you can do from CLI is mess with `HardwareStatus()` (read about it more in Utilities). This is aliased to the command `dfhardware`, and you can run any of the methods as follows:

# In[ ]:


dfhardware get_status viz


# In[ ]:


dfhardware get_status down


# In[ ]:


dfhardware MarkUnitDown Dragonfly301


# In[ ]:


dfhardware MarkAccessibleUnitsUp


# In[ ]:


dfhardware MarkAllUnitsDown


# For now, that's about it, but I may add some more over time. 
