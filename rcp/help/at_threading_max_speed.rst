Threading Max Speed (Steps/s)
=============================

The maximum servo speed allowed during the threading cut itself.

How It Works
------------

When a threading pass begins, the firmware drives the saddle at the
speed required by the spindle RPM and selected pitch. This value acts
as a hard cap — the servo will not exceed it regardless of how fast
the spindle is turning.

The system also uses this limit to calculate the **maximum allowable
spindle RPM** for the selected pitch. If the spindle is turning too
fast when you press Cut, a warning is shown and the cut is blocked
until the spindle speed is reduced.

Spindle Speed Limit
-------------------

The relationship between spindle RPM and required servo speed is:

  required steps/s = (spindle RPM / 60) × pitch × steps per mm × scale/servo ratio

A higher threading max speed allows a faster spindle, but the machine
must be rigid enough to handle the increased feed rate.

Typical Ranges
--------------

===================  ======================
Servo Max Speed      Typical Threading Speed
===================  ======================
1000 steps/s         500–1000 steps/s
2000 steps/s         1000–2000 steps/s
3000 steps/s         1500–3000 steps/s
===================  ======================

Notes
-----

- Value is clamped to the servo max speed
- For coarse pitches (> 2 mm / < 13 TPI), consider a lower value to
  reduce chatter and tool load
- If the system warns that your spindle is too fast, either reduce
  spindle RPM or increase this setting (within your machine's limits)
- See also: Servo Max Speed in the Servo setup screen
