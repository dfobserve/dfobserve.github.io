#!/usr/bin/env python
# coding: utf-8

# # DFObserve Guide
# 
# This documentation is intended to accompany the docs/api to provide general practices for using the `DFObserve` package. 
# 
# Let's dive in! 
# 
# ## Modules 
# 
# `DFObserve` is currently split into four modules: `observing`, `webserver`, `utils`, and `standards`. 
# 
# - `observing` contains the tools for setting up observations, including the `Observation` class and `AutoObserve` class. 
# - `webserver` contains tools for using the webserver to interact with the instrument.
# - `utils` contains base level convenience functions, stored in submodules such as `CameraUtils`, `FilterTilterUtils`, etc... 
# - `standards` contains tools for selecting standard stars (or other objects) for use during observing. 
# 
# In the pages on this site, we'll cover each of these in some detail, with example usage. But from a top-level, "perfect world" scenario, one won't interact with much more than the `Observation` and `AutoObserve` classes. So that will be our first stop!
