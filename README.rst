========
Overview
========


Python wrapper for strategies originally written in Fortran.

* Free software: MIT license

Installation
============

To use this library the original Fortran code must be compiled:
https://github.com/Axelrod-Python/TourExec.

::

    pip install axelrod-fortran


Usage
=====

Running a match:

.. code-block:: python

   >>> import axelrod_fortran as axlf
   >>> import axelrod as axl
   >>> p1 = axlf.Player('k31r')
   >>> p2 = axlf.Player('k33r')
   >>> match = axl.Match((p1, p2), turns=5)
   >>> match.play()
   [(C, C), (C, C), (C, D), (C, D), (C, C)]

Contributing
============

Please see `CONTRIBUTING.rst` for details about installing for development and
running the test suite.
