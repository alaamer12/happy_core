API Reference
=============

This page contains detailed API reference documentation for all True-Core modules.

.. raw:: html

   <div class="banner-container">
      <img src="_static/light_true_banner.png" class="banner light-banner" alt="True Storage Banner">
      <img src="_static/dark_true_banner.png" class="banner dark-banner" alt="True Storage Banner">
   </div>


.. module:: true
   :no-index:

Collections and File System
---------------------------

.. module:: true.collections
   :no-index:

File System Objects
~~~~~~~~~~~~~~~~~~~

.. autoclass:: File
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. autoclass:: Directory
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

OSUtils
~~~~~~~

.. autoclass:: OSUtils
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Time Management
---------------

.. module:: true.time
   :no-index:

Time
~~~~

.. autoclass:: Time
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Event
~~~~~

.. autoclass:: Event
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Schedule
~~~~~~~~

.. autoclass:: Schedule
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Regular Expressions
-------------------

.. module:: true.re
   :no-index:

Username Patterns
~~~~~~~~~~~~~~~~~

.. data:: USERNAME_ONLY_LETTERS_MIN_3
   :no-index:

.. data:: USERNAME_LETTERS_AND_NUMBERS_MIN_3
   :no-index:

.. data:: USERNAME_WITH_UNDERSCORES_MIN_3
   :no-index:

.. data:: USERNAME_WITH_DASHES_AND_UNDERSCORES_MIN_3
   :no-index:

.. data:: USERNAME_NO_CONSECUTIVE_SPECIAL_CHARS
   :no-index:

.. data:: USERNAME_STARTS_WITH_LETTER
   :no-index:

.. data:: USERNAME_MAX_20_CHARACTERS
   :no-index:

.. data:: USERNAME_NOT_NUMERIC_ONLY
   :no-index:

.. data:: USERNAME_NO_PREFIX_SUFFIX
   :no-index:

.. data:: USERNAME_INCLUDE_LETTER_AND_NUMBER
   :no-index:

Password Patterns
~~~~~~~~~~~~~~~~~

.. data:: PASSWORD_MIN_8
   :no-index:

.. data:: PASSWORD_MIN_8_WITH_NUMBER
   :no-index:

.. data:: PASSWORD_MIN_8_UPPER_LOWER_NUMBER
   :no-index:

.. data:: PASSWORD_MIN_8_UPPER_LOWER_NUMBER_SPECIAL
   :no-index:

.. data:: PASSWORD_NO_WHITESPACE
   :no-index:

Email Patterns
~~~~~~~~~~~~~~

.. data:: EMAIL_BASIC
   :no-index:

.. data:: EMAIL_RFC_5322
   :no-index:

.. data:: EMAIL_WITH_SUBDOMAINS
   :no-index:

.. data:: EMAIL_WITH_UNICODE
   :no-index:

Exceptions
----------

.. module:: true.exceptions
   :no-index:

Enum Exceptions
~~~~~~~~~~~~~~~

.. autoexception:: InvalidEnumTypeError
   :no-index:

.. autoexception:: EnumMetadataError
   :no-index:

.. autoexception:: EnumValidationError
   :no-index:

.. autoexception:: EnumTypeError
   :no-index:

File System Exceptions
~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: StorageFullError
   :no-index:

.. autoexception:: ItemNotFoundError
   :no-index:

.. autoexception:: RestoreError
   :no-index:

Type Exceptions
~~~~~~~~~~~~~~~

.. autoexception:: UnsuitableBigIntError
   :no-index:

.. autoexception:: UnsuitableBigDecimalError
   :no-index:

.. autoexception:: InvalidUUIDError
   :no-index:

.. autoexception:: InvalidUUIDVersionError
   :no-index:

.. autoexception:: InvalidULIDError
   :no-index:

Time Exceptions
~~~~~~~~~~~~~~~

.. autoexception:: ScheduleError
   :no-index:

.. autoexception:: ScheduleConflictError
   :no-index:

.. autoexception:: ScheduleValidationError
   :no-index: