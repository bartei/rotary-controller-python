Reversing Speed (Steps/s)
=========================

The servo speed used when the retract button is held, and during the
retract phase of the automatic go-to-start sequence.

How It Works
------------

**Retract button (manual):** while held, the saddle jogs away from the
workpiece at this speed. This is useful when you want to move the saddle
clear of the workpiece — for example to test thread fit you might want to move 
the saddle out of the way further than the start position. Releasing the button stops the saddle.

**Go-to-start (automatic):** when you press Go to start between passes,
the system automatically retracts past the start position at this speed
before slowing to the preload/adjust speed to return precisely to start.
You do not need to use the retract button for normal between-pass
operation — the go-to-start button handles the full sequence.

Guidelines
----------

- This speed can be set close to your servo max speed — quick
  retraction saves time on each pass, especially for longer threads
- There is no requirement for this to be slow; accuracy is not
  critical during retraction
- Higher values reduce the time between passes

Typical Ranges
--------------

===================  ===================
Servo Max Speed      Typical Reversing Speed
===================  ===================
500 steps/s          250–500 steps/s
1000 steps/s         500–1000 steps/s
2000 steps/s         1000–2000 steps/s
3000 steps/s         1500–3000 steps/s
===================  ===================

**Typical setting:** 50–100% of your servo max speed.

Notes
-----

- Value is clamped to the servo max speed — it cannot exceed it
- The Reversing/Adjusting Acceleration setting controls how quickly
  the saddle ramps up and down to this speed
