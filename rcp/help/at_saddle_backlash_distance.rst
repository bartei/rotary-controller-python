Saddle Backlash Distance
========================

The total free play in the saddle (Z-axis) drive — the distance the
handwheel travels before the saddle actually begins to move when
direction is reversed.

How It Is Used
--------------

This distance is used to calculate the retract and preload move
distances in the go-to-start sequence:

- **Retract:** moves 1.5× this distance past the thread start
- **Preload:** advances 1.25× this distance back toward the start
  (to fully load the drive in the cutting direction)
- **Adjust:** final fine move to land on the exact start position

Setting this correctly ensures the drive is fully preloaded before
the threading cut begins, eliminating backlash-induced position error
on the first stroke of each pass.

How to Measure
--------------

1. Engage the half nut on the lathe
2. Turn the handwheel in the cutting direction until it stops
   (the lead screw is loaded in one direction)
3. Zero the DRO
4. Turn the handwheel in the opposite direction until it stops
5. Read the DRO value — this is your backlash distance
6. Repeat at several points along the saddle travel and average
   the readings for accuracy

Common Values
-------------

Backlash varies widely between machines. Freshly adjusted or
re-fitted nuts have less backlash; worn machines may have
significantly more.

Notes
-----

- Set the Metric Distances toggle above to match the unit you intend
  to use before entering this value
- **Too low:** drive is not fully preloaded → first cut of each pass
  may be shallower than expected
- **Too high:** unnecessarily long retract and preload moves, slowing
  down each pass
