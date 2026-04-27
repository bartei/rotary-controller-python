Saddle Encoder Stability Samples
=================================

The number of consecutive stable encoder readings required before the
saddle is confirmed as fully stopped.

How It Works
------------

After a servo move, the system polls the saddle encoder on each
control tick. A reading is considered "stable" if the change in
position since the last reading is within the Saddle Encoder Stability
Tolerance. This setting specifies how many stable readings in a row
must be observed before the wizard advances.

This guards against brief pauses in motion (such as when a fast-
moving saddle momentarily slows through the target) being mistakenly
treated as a full stop.

Guidelines
----------

- **Higher value:** more conservative — requires more consecutive
  stable ticks, reducing false stops; adds a small delay after motion
- **Lower value:** faster response after the saddle stops, but may
  advance the wizard too early if the saddle is still settling

Typical Range
-------------

=========  =========================================================
Samples    Behaviour
=========  =========================================================
2          Minimal confirmation — fast but may trigger on a brief lull
3          Default — suitable for most setups
4–5        More reliable on machines with resonance or encoder noise
=========  =========================================================

Notes
-----

- If the wizard advances before the saddle has fully stopped, increase
  this value
- If the wizard is slow to advance after motion completes, reduce it
- Works in conjunction with Saddle Encoder Stability Tolerance
- Value must be a positive integer
