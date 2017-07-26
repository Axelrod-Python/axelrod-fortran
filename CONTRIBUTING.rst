============
Contributing
============

To set up `axelrod-fortran` for local development:

1. Fork `axelrod-fortran <https://github.com/meatballs/axelrod-fortran>`_
   (look for the "Fork" button).
2. Clone your fork locally::

    git clone git@github.com:your_name_here/axelrod-fortran.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. To install a development version of the library::

    python setup.py develop

   For this to work you also need the original Fortan code installed.
   Instructions for this are available:
   https://github.com/Axelrod-Python/TourExec

5. To run tests, `py.test` is used as a test runner::

    pip install pytest

   To run the tests::

    pytest
