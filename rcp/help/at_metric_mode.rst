Metric Mode
===========

Selects the unit system for thread pitch in the threading settings.

When ON, pitches are in **millimetres** (metric threads — ISO, ACME).
When OFF, pitches are in **threads per inch** (TPI — imperial threads,
Unified, Whitworth, ACME).

Effect on Other Settings
------------------------

Changing this setting rebuilds both the pitch dropdown and the
available thread type options, as some thread types are only
defined for metric or imperial pitch systems.

This setting does **not** affect:

- DRO display units (set in the Formats screen)
- Backlash distance units (set by Metric Distances in ELS Setup)
- Encoder or servo configuration

Which to Choose
---------------

==========  ==========================================
Mode        Use when
==========  ==========================================
ON (MM)     Cutting ISO metric threads (M-series)
OFF (TPI)   Cutting Unified (UNC/UNF) or Whitworth threads
==========  ==========================================

ACME threads are available in both modes — select the mode that
matches the pitch specification of your lead screw or part drawing.

Notes
-----

- Switching this resets the pitch dropdown to the first available
  option; re-select your desired pitch after changing
