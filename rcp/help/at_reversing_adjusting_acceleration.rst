Reversing / Adjusting Acceleration (Steps/s²)
=============================================

How quickly the servo ramps up and slows down during retraction,
preload, and adjust moves — the non-cutting phases of the threading
cycle.

How It Works
------------

This acceleration is applied to three moves:

1. **Retract:** saddle moves backward after a threading pass
2. **Preload:** saddle advances to load drive backlash before returning
   to start
3. **Adjust:** final fine move to the exact thread start position

For these positioning moves, smooth and controlled motion is more
important than speed. A lower acceleration produces gentler
deceleration into the start position, reducing overshoot.

Guidelines
----------

- Keep this value lower than the threading acceleration — the priority
  here is accurate stopping, not fast ramp-up
- Too high: the saddle may overshoot the start position, requiring
  the system to detect it is out of position and abort the cut
- Too low: very gradual starts and stops; the retract and preload
  moves feel sluggish

Typical Range
-------------

**Typical setting:** 50–100% of your Reversing Speed value.

For example, if Reversing Speed = 1000 steps/s, set this to
500–1000 steps/s².

Notes
-----

- This is a separate setting from Threading Acceleration, which
  handles the actual cutting moves
- If cuts are frequently aborted with a "not at valid start position"
  warning, try reducing this value to improve stopping accuracy
