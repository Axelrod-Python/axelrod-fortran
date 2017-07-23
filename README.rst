========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/axelrod-fortran/badge/?style=flat
    :target: https://readthedocs.org/projects/axelrod-fortran
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/meatballs/axelrod-fortran.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/meatballs/axelrod-fortran

.. |codecov| image:: https://codecov.io/github/meatballs/axelrod-fortran/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/meatballs/axelrod-fortran

.. |version| image:: https://img.shields.io/pypi/v/axelrod-fortran.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/axelrod-fortran

.. |commits-since| image:: https://img.shields.io/github/commits-since/meatballs/axelrod-fortran/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/meatballs/axelrod-fortran/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/axelrod-fortran.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/axelrod-fortran

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/axelrod-fortran.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/axelrod-fortran

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/axelrod-fortran.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/axelrod-fortran


.. end-badges

Python wrapper for strategies originally written in Fortran

* Free software: MIT license

Installation
============

::

    pip install axelrod-fortran

Documentation
=============

https://axelrod-fortran.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
