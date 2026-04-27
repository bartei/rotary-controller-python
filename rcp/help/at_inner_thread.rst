Inner Thread
============

When enabled, the threading wizard drives the cross slide outward
for each cutting pass instead of inward, for cutting an internal
(female) thread inside a bore.

External vs Internal
--------------------

**OFF (default) — External thread:**
The cross slide advances inward (toward the workpiece centreline) to
increase cutting depth. Used for cutting threads on the outside of a
shaft or bar.

**ON — Internal thread:**
The cross slide advances outward (away from the centreline) to
increase cutting depth into a pre-bored hole. Used for cutting threads
on the inside of a hole.

Preparation
-----------

Before using the threading wizard for an internal thread:

1. Drill or bore the hole to the correct tapping diameter for the
   chosen thread and pitch
2. Ensure the boring bar or threading insert clears the hole diameter
   through the full thread length

Thread Depth
------------

The auto-calculated thread depth applies in both modes. In inner
thread mode, this depth is taken outward from the bore wall.

Notes
-----

- Changing this setting reverses the cross-slide direction check in
  the wizard — the "retracted" state and "at cutting depth" condition
  are both interpreted relative to the bore wall, not the centreline
- This setting does not affect the saddle (Z) direction — that is
  controlled by Left Hand Thread
