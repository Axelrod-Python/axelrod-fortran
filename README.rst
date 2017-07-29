========
Overview
========


Python wrapper for strategies originally written in Fortran

* Free software: MIT license

Installation
============

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

Reproducing Axelrod's second tournament:

.. code-block:: python

   import axelrod as axl
   from axelrod_fortran.strategies import characteristics
   from axelrod_fortran.player import Player

   players = [Player(name) for name in characteristics.keys()
              if characteristics[name]["original_rank"] is not None]

   print(len(players), "players")

   tournament = axl.Tournament(players, repetitions=100)
   results = tournament.play(processes=4)
   results.write_summary('summary.csv')
   plot = axl.Plot(results)
   plot.save_all_plots("second_tournament")

Contributing
============

Please see `CONTRIBUTING.rst` for details about installing for development and
running the test suite.
