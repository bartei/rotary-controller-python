Saddle Encoder Stability Tolerance (Counts)
============================================

The maximum allowed variation in saddle encoder counts between
consecutive readings before the saddle is considered stationary.

How It Works
------------

After every servo move (retract, preload, adjust), the system polls
the saddle encoder to confirm it has fully come to rest. On each poll,
it checks whether the absolute change in encoder position since the
last reading is within this tolerance. When the change stays within
tolerance for the required number of samples (see Saddle Encoder
Stability Samples), the saddle is declared stopped and the wizard
advances to the next step.

Guidelines
----------

- **Smaller value:** stricter definition of "stopped" — use on rigid
  machines where the saddle truly stops quickly with minimal bounce
- **Larger value:** more forgiving — useful if the encoder shows slight
  jitter or the saddle takes time to settle completely

Typical Range
-------------

=======  ====================================================
Counts   Behaviour
=======  ====================================================
1        Default — very strict; typical for clean setups
2–3      Slightly more forgiving; reduces false "still moving"
4+       Only needed if encoder is noisy or saddle bounces
=======  ====================================================

Notes
-----

- If the wizard seems to hang after a move and never advances, try
  increasing this value by 1–2 counts
- This setting works together with Saddle Encoder Stability Samples —
  both must be satisfied before the saddle is considered stopped
- Value must be a positive integer
