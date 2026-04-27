Preload / Adjust Speed (Steps/s)
================================

The servo speed used when positioning the saddle back to the thread
start during the go-to-start sequence.

How It Works
------------

After retracting past the start position, the system performs two
precision moves before the next cut:

1. **Preload move:** the saddle advances in the cutting direction to
   take up the drive backlash (1.25× the configured backlash distance)
2. **Adjust move:** the saddle makes a final fine move to land exactly
   at the thread start position

Both moves use this speed. Slow, controlled movement here ensures the
saddle lands accurately at the start and the drive is fully loaded.

Guidelines
----------

- Keep this speed low — positional accuracy is the priority here,
  not throughput
- Too fast risks overshooting the start position or inadequate
  backlash preloading, which leads to a thread out of phase on the
  next pass

Typical Ranges
--------------

===================  =====================
Servo Max Speed      Typical Preload Speed
===================  =====================
500 steps/s          50–75 steps/s
1000 steps/s         100–150 steps/s
2000 steps/s         200–300 steps/s
3000 steps/s         300–450 steps/s
===================  =====================

**Typical setting:** 10–15% of your servo max speed.

Notes
-----

- Value is clamped to the servo max speed
- If the saddle consistently overshoots the start position, reduce
  this value
- See also: Saddle Backlash Distance, Reversing/Adjusting Acceleration
