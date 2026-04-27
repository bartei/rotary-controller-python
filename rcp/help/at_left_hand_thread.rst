Left Hand Thread
================

When enabled, the saddle feed direction is reversed so the thread
tightens when rotated counter-clockwise (viewed from the end).

Standard vs Left Hand
---------------------

**OFF (default) — Right hand thread:**
The saddle moves toward the headstock during the cut. The thread
tightens by turning clockwise.

**ON — Left hand thread:**
The saddle moves away from the headstock during the cut. The thread
tightens by turning counter-clockwise.

Common Uses
-----------

- Left-side pedal crank threads on bicycles
- Left-hand adjusters and lock nuts (to prevent loosening under
  rotation)
- Specialty jigs and fixtures
- Turnbuckle bodies (one end right, one end left)

What Changes
------------

Enabling left hand thread reverses the ELS sync ratio sign on the
spindle axis, causing the servo to drive in the opposite direction
relative to spindle rotation. The displayed sync ratio reflects this.

Notes
-----

- The spindle must still be turning in the same direction as for a
  right-hand thread — do not reverse the lathe spindle; the firmware
  handles feed direction reversal
- The threading wizard start and stop positions use the same
  convention; set your start position where the thread begins and
  stop position where it ends, in the physical direction of travel
