:py:mod:`dfobserve.utils.FlipFlatUtils`
=======================================

.. py:module:: dfobserve.utils.FlipFlatUtils

.. autoapi-nested-parse::

   FlipFlatUtils: Functions to open/close all or a subset of flip flats using the web server.



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   dfobserve.utils.FlipFlatUtils.AllCloseFlipFlats
   dfobserve.utils.FlipFlatUtils.AllOpenFlipFlats
   dfobserve.utils.FlipFlatUtils.OpenFlipFlats
   dfobserve.utils.FlipFlatUtils.CloseFlipFlats



.. py:function:: AllCloseFlipFlats(verbose=True, which='science', port: str = '/dev/ttyUSB2', **kwargs)

   :param verbose: whether to show the return from the webrequest. Default: True
   :type verbose: bool (optional)
   :param \*\*kwargs: additional keyword arguments recognized by SendWebRequestNB
   :type \*\*kwargs: (optional)


.. py:function:: AllOpenFlipFlats(verbose=True, which='science', port: str = '/dev/ttyUSB2', **kwargs)

   :param verbose: whether to show the return from the webrequest. Default: True
   :type verbose: bool (optional)
   :param \*\*kwargs: additional keyword arguments recognized by SendWebRequestNB
   :type \*\*kwargs: (optional)


.. py:function:: OpenFlipFlats(unit_list: list, port: str = '/dev/ttyUSB2', verbose: bool = True)

   Open only SOME flip flats. Does them one by one at the moment

   :param unit_list: list of units to open flip flats for. Can be in form [301,303,309] or ['Dragonfly301','Dragonfly306']
   :type unit_list: list
   :param verbose: whether to show the return from the webrequest. Default: True
   :type verbose: bool (optional)


.. py:function:: CloseFlipFlats(unit_list: list, port: str = '/dev/ttyUSB2', verbose: bool = True)

   Close only SOME flip flats. Currently does them one by one.

   :param unit_list: list of units to open flip flats for. Can be in form [301,303,309] or ['Dragonfly301','Dragonfly306']
   :type unit_list: list
   :param verbose: whether to show the return from the webrequest. Default: True
   :type verbose: bool (optional)


