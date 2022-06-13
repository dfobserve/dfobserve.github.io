:py:mod:`dfobserve.utils.NetworkUtils`
======================================

.. py:module:: dfobserve.utils.NetworkUtils

.. autoapi-nested-parse::

   Tools for getting information about the network of raspberry pis.



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.NetworkUtils.get_network_df
   dfobserve.utils.NetworkUtils.get_status_df



.. py:function:: get_network_df(net_path: str = '/mnt/c/Windows/System32/net.exe', verbose: bool = False) -> pandas.DataFrame

   Obtains the ip addresses of the pis and returns a dataframe.

   :param net_path: path to the net.exe
   :type net_path: str (optional)
   :param verbose: whether to display the dataframe (default: False)
   :type verbose: bool (optional)

   :returns: **network_df** -- df containing the ip addresses, mount volumes, etc.
   :rtype: pandas.DataFrame


.. py:function:: get_status_df(hardware_config_path='/home/dragonfly/git/Dragonfly-Configuration/DRAGONFLY_HARDWARE_TEMPLATE.txt', verbose=False) -> pandas.DataFrame

   Return a dataframe with the current up/down info and IP addresses of each pi

   :param hardware_config_path: location of the hardware config file
   :type hardware_config_path: str (optional)
   :param verbose: whether to display the read-in dataframe (default: False)
   :type verbose: bool (optional)

   :returns: **status_df** -- df containing IP addresses and UP/Down status (and other info)
   :rtype: pandas.DataFrame


