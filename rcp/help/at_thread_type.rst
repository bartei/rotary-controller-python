Thread Type
===========

The thread profile geometry — the cross-sectional shape of the
thread form being cut.

This setting determines:

- The formula used to auto-calculate cutting depth
- The compound infeed angle (if compound infeed mode is enabled)

Available Types
---------------

ISO Metric
^^^^^^^^^^
Standard metric fastener thread. 60° included angle (30° half-angle).
Covers all M-series screws and bolts per ISO 68-1.

Unified
^^^^^^^
Standard US/imperial fastener thread (UNC and UNF). Also a 60° included
angle. Per ASME B1.1. Use this for most inch-dimensioned fasteners.

Whitworth
^^^^^^^^^
Older British standard thread (BSW and BSF). 55° included angle
(27.5° half-angle). Used on older British-made machines and
replacement parts for vintage equipment.

ACME
^^^^
Trapezoidal thread profile. 29° included angle (14.5° half-angle).
Per ASME B1.5. Commonly used for lead screws, vise screws, and
other power transmission applications where self-locking and
strength are important.

Thread Depth Formulas
---------------------

==========  ===========  ========================
Type        Factor       Depth formula
==========  ===========  ========================
ISO Metric  0.61343      depth = 0.61343 × pitch
Unified     0.64952      depth = 0.64952 × pitch
Whitworth   0.6403       depth = 0.6403 × pitch
ACME        0.5          depth = 0.5 × pitch
==========  ===========  ========================

*Depth is radial. If Cross Slide Diameter Mode is ON, this value is
doubled.*

Notes
-----

- ACME is available in both metric and imperial pitch modes
- Changing thread type updates the compound infeed angle automatically
  when compound infeed mode is enabled
