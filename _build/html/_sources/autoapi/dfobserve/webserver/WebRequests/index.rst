:py:mod:`dfobserve.webserver.WebRequests`
=========================================

.. py:module:: dfobserve.webserver.WebRequests

.. autoapi-nested-parse::

   Functions for Using the Webserver to interact with the instrument.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   dfobserve.webserver.WebRequests.Status
   dfobserve.webserver.WebRequests.WebRequestSummary
   dfobserve.webserver.WebRequests.APIResponse
   dfobserve.webserver.WebRequests.WrapDF



Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.webserver.WebRequests.NewSendCommand
   dfobserve.webserver.WebRequests.SendCommand
   dfobserve.webserver.WebRequests.SendWebRequestNB
   dfobserve.webserver.WebRequests.ParseResponse



.. py:function:: NewSendCommand(command: str, ip: str, port=3000, params: dict = {}, timeout=(5, 5))


.. py:class:: Status(unit)

   .. py:method:: __repr__(self)

      Return repr(self).


   .. py:method:: __str__(self)

      Return str(self).


   .. py:method:: construct_dataframes(self)



.. py:function:: SendCommand(command: str, ip: str, timeout_seconds: int = 10, name: str = None, verbose: bool = False)


.. py:function:: SendWebRequestNB(command: str = None, which: str = 'all', skip: list = [], ha_command: str = None, oiii_command: str = None, ha_off_command: str = None, oiii_off_command: str = None, OH_command: str = None, OH_off_command: str = None, all_flathaving_command: str = None, verbose: bool = True, wait_for_response: bool = True, timeout_global: int = 120, timeout_seconds: int = 10, dryrun=False, hardware_config_file=None, **kwargs)

   Send a webrequest to the array but divy up commands by type if requested.
   No required inputs, but if it is run with no inputs, a webrequest will not be sent.

   :param command: command to broadcast to units. This option acts in concert with the `which` keyword argument,
                   which determines where the command will be sent. If further separate commands are needed, use
                   the individually coded keywords. (Default: None)
   :type command: str, optional
   :param which:
                 which units to broadcast the `command` to. Options include
                     `'all'`: send to all lenses. (for example, make all lenses take a 0 second exposure)

                     `'science'`: send to the H-alpha and OIII lenses only. All others will idle.

                     `'science offs'`: send to the offs for H-alpha and OIII only.

                     `'OH'`: send command to the OH on and OH off units
                     `'halpha'`: send to halpha units only
                     `'oiii'`: send to the OIII units only
                 Note that the supplication of any of the more specific keyword args (e.g., `OH_command`) will
                 overwrite the command being sent when this option is used. (Default: 'all')
   :type which: str, optional
   :param skip: any units to skip when sending this command (e.g., those that are down). Should be list of str like 'Dragonfly301'
   :type skip: list, default: []
   :param ha_command: command to send only to the Halpha units. (Default: None)
   :type ha_command: str, optional
   :param oiii_command: command to send only to the OIII units. (Default: None)
   :type oiii_command: str, optional
   :param ha_off_command: command to send only to the offband units of Halpha. (Default: None)
   :type ha_off_command: str, optional
   :param oiii_off_command: command to send only to the offband units of OIII. (Default: None)
   :type oiii_off_command: str, optional
   :param OH_command: command to send only to the OH skyline monitoring units. (Default: None)
   :type OH_command: str, optional
   :param OH_off_command: command to send only to the OH skyline off band units. (Default: None)
   :type OH_off_command: str, optional
   :param all_flathaving_command: command to send to all units with a flip flat attached. (Default: None)
   :type all_flathaving_command: str, optional
   :param verbose: print out info along the way. (Default: True)
   :type verbose: bool, default: True
   :param wait_for_response: wait for all machines to send a response before returning (until timeout). (Default: True)
   :type wait_for_response: bool, default: True
   :param timeout_global: time in seconds to wait while pending machines finish tasks before exiting. (Default: 120)
   :type timeout_global: int, default: 120
   :param timeout_seconds: time in seconds after which to close the connection and mark a machine as failed. (Default: 10)
   :type timeout_seconds: int, default: 10
   :param dryrun: don't execute the command, but show what commands will be sent to which IP addresses. (Default: False)
   :type dryrun: bool, default: False

   :returns: **result_df or WebRequestSummary** -- dataframe (or wrapped version) containing the webrequest results.
   :rtype: pandas.DataFrame


.. py:class:: WebRequestSummary(webrequest_df: pandas.DataFrame)

   .. py:method:: get_response_by_ip(self, ip: str)

      Obtain the APIResponse object for a given unit

      :param ip: IP address of the unit
      :type ip: str


   .. py:method:: get_response_by_name(self, name: str)

      Obtain the APIResponse object for a given unit

      :param ip: IP address of the unit
      :type ip: str


   .. py:method:: __str__(self)

      Return str(self).


   .. py:method:: __repr__(self)

      Return repr(self).



.. py:class:: APIResponse(response_dict)

   .. py:method:: __repr__(self)

      Return repr(self).


   .. py:method:: __str__(self)

      Return str(self).


   .. py:method:: info(self, verbose=False)

      Prints the accessible fields (attributes) of the object.

      :param verbose: show just the field names, or also all the values
      :type verbose: bool, default: False


   .. py:method:: construct_dataframes(self)

      Constructs individual DataFrames for each main field in the status response, and wrap them.



.. py:function:: ParseResponse(response, return_type='dict')

   Parses the byte-string response from the webserver into either a dictionary or an API object.

   :param response: response from the webserver (generally a status)
   :type response: byte
   :param return type: type of object to return. Options are 'dict' or 'API'.
   :type return type: str, default: 'dict'


.. py:class:: WrapDF(df)

   Dataframe wrapper that provides a 'get' method.

   .. py:method:: __repr__(self)

      Return repr(self).


   .. py:method:: __str__(self)

      Return str(self).


   .. py:method:: get(self, field)

      Get the value of an associated field. Wrapper for a loc type command.

      :param field: name of the field to get value for.
      :type field: str



