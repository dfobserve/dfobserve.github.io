#!/usr/bin/env python
# coding: utf-8

# # Reponses from the Webserver 
# 
# `DFObserve` contains a few wrapper classes that make interacting with the output of a WebRequest more functional. Generally these are used "under the hood," but let's go over how it works for completeness (as well as for adding new functions and features). 

# In[1]:


from dfobserve.webserver import SendWebRequestNB


# We've imported the primary SendWebRequest function. Let's ask for a 'status' from the server:

# In[2]:


status = SendWebRequestNB('status')


# We can see the verbose reponse from the instrument above. It sent the status command to all IPs, and then we got responses, which in this case were 9 successes and 1 machine down. Notice in the `full_response` column, the successful responses contain `APIResponse` objects. Let's look at one.
# 
# To do so, we need to retrieve it from the `status` object, which is an instance of `WebRequestSummary`. We can do this easily either by dot notation and the unit name, or using the `get_response()` method which takes in the desired IP address.

# In[3]:


df301 = status.Dragonfly301
df301


# The `APIResponse` object has a handy `info()` method which can tell us its attributes:

# In[4]:


df301.info()


# So we can now access, say, `CameraProperties` by dot notation:

# In[5]:


df301.CameraProperties


# Each field (e.g., `CameraProperties`) is also a wrapped object (technically, the `WrapDF` object), meaning we can once again dot-notate to get a value out:

# In[6]:


df301.CameraProperties.FocusModel


# For completeness, there is also an explicit `get()` method, e.g., 

# In[7]:


df301.CameraProperties.get('FocusModel')


# Finally, the `APIResponse.info()` method introduced above has a verbose mode that will print the fields AND their internals, if you want to see everything all at once:

# In[8]:


df301.info(verbose=True)


# You may notice that all of the printouts of these objects appear as pandas DataFrames. Currently, `SendWebRequestNB` constructs DataFrames to send, and parses responses into DataFrames as well. The raw DataFrames can be accessed in either a `WebRequestSummary` object or in an `APIResponse` object or in a `WrapDF` object via the `df` attribute. This is not strictly speaking useful unless you prefer to work with a DataFrame for some particular reason. Note that the *attributes* of each object are read off of the DataFrame upon instantiation, and currently, do not support @property tags to read them dynamically from the DataFrame. Hence, one can modify values in the DataFrame and make them inconsistent with the values in the same-named attribute. 
# 
# I plan to fix this in the future but for now it is not a huge concern because *responses* from the Webserver should be read-only in practice anyway. At least at the initial response layer.  
