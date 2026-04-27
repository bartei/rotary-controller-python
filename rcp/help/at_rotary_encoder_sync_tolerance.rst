Rotary Encoder Sync Tolerance (Counts)
=======================================

Defines the ±window (in spindle encoder counts) around the reference
spindle angle at which each threading pass re-engages.

How It Works
------------

When you press Cut for the first time, the firmware records the current
spindle angle as the **phase reference** for this thread. For every
subsequent pass, the firmware waits until the spindle returns to within
±tolerance counts of that same reference angle before enabling the
servo threading move.

This phase-locking ensures every pass starts at the same point in the
spindle rotation, so successive cuts follow the same helical path and
do not cross-thread.

Units
-----

The value is in **spindle encoder counts** — the same scale as your
spindle encoder's counts per revolution (spindleCountsPerRev).

To convert to degrees: **tolerance_degrees = (tolerance / counts_per_rev) × 360**

Example: 1000-count encoder, tolerance = 5 → ±1.8° window.

Guidelines
----------

- **Smaller value:** tighter re-engagement angle — more consistent
  thread helix, but may delay the trigger if the encoder has noise
- **Larger value:** wider window — triggers more readily but the start
  angle may vary slightly between passes

Typical Range
-------------

===========  ==============================================================
Tolerance    Effect
===========  ==============================================================
1–3 counts   Very tight — use only if encoder signal is clean
5 counts     Default — suitable for most setups
10–15 counts Wider window — useful if threading start is unreliable
===========  ==============================================================

Notes
-----

- If threading passes never start (the servo just waits), increase
  this value to widen the trigger window
- If cut helix alignment is poor between passes, reduce this value
- Value must be a positive integer
