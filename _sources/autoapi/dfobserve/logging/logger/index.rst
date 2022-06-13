:py:mod:`dfobserve.logging.logger`
==================================

.. py:module:: dfobserve.logging.logger

.. autoapi-nested-parse::

   General Use logger for keeping track of what goes on during an observation night.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   dfobserve.logging.logger.Logger




.. py:class:: Logger(save_path=None)

   .. py:method:: set_file(self, fname)


   .. py:method:: setup_db(self, name=None)


   .. py:method:: write_db(self, webrequest_summary)


   .. py:method:: info(self, s)


   .. py:method:: warning(self, s)


   .. py:method:: vspace(self, n)


   .. py:method:: section(self, s)



