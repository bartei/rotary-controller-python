Saddle Backlash Cushion
=======================

A small distance value that serves two safety roles in the threading
wizard.

Role 1 — Minimum Thread Length
--------------------------------

The stop position you set in the wizard must be at least this distance
from the start position. If the stop is closer than the cushion, the
system rejects it.

This prevents attempting to cut a thread so short that the preload
and go-to-start sequence cannot work reliably within the available
length.

Role 2 — Start Position Validation
-----------------------------------

Before each threading cut begins, the system checks that the saddle
is within this distance of the configured start position. If the
saddle has drifted further away (e.g. overshot during preload), the
cut is aborted and you are returned to the go-to-start step.

This ensures every cut starts from a consistent position, which is
especially important for fine pitches where a small positional error
shifts the thread by a significant fraction of the pitch.

How to Set
----------

Use a small fraction of your Saddle Backlash Distance value, and
keep it smaller than the shortest pitch you intend to cut:

- Example: 2 mm backlash → 0.1 mm cushion
- Rule of thumb: cushion < backlash distance / 10
- Also ensure: cushion < your minimum thread pitch

Too Large
---------

- Short threads are unnecessarily rejected
- A larger tolerance is allowed at the start position — the saddle
  may be further off the ideal start, which for fine pitches can cause
  the thread to start at the wrong phase and damage the workpiece

Too Small
---------

- Higher accuracy is required from the go-to-start sequence
- Depending on the machine, it may be difficult to consistently land
  within a very tight tolerance — this causes frequent false aborts
  before cuts

Notes
-----

- Set the Metric Distances toggle above to match the unit before
  entering this value
- If you see repeated "not at valid start position" warnings, consider
  slightly increasing the cushion or reducing the preload/adjust speed
