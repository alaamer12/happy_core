Welcome to True Core's documentation!
=====================================

.. raw:: html

   <div class="banner-container">
      <img src="_static/light_true_banner.png" class="banner light-banner" alt="True Storage Banner">
      <img src="_static/dark_true_banner.png" class="banner dark-banner" alt="True Storage Banner">
   </div>

.. image:: https://img.shields.io/badge/python-3.7%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://choosealicense.com/licenses/mit/


True is a comprehensive utility toolkit designed for Python developers seeking clean, efficient, and maintainable solutions.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   api_reference
   examples
   migration_v0.2.0

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api
   modules/collections
   modules/time
   modules/re
   modules/toolkits

.. toctree::
   :maxdepth: 2
   :caption: Project Info

   changelog
   releases

.. toctree::
   :maxdepth: 2
   :caption: See Also 

   packages
   packages_references

.. warning::
   **Breaking Changes in Version 0.2.0**

   Several major components have been moved to separate packages:

   - Enumeration functionality → ``true-enumeration`` package
   - Type system → ``true-types`` package
   - ``DummyFile`` → ``true-blobs`` package
   
   Some components have been removed:
   
   - ``Pointer`` class has been removed entirely
   - ``Recyclebin`` functionality has been temporarily removed
   
   Please see :doc:`releases/0.2.0` for migration instructions.

Features
--------

* Time Handling
* Regular Expressions
* File Operations
* Exception Handling

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
