Cross Slide Diameter Mode
=========================

Tells the system how your cross-slide scale is physically configured —
whether it reads full diameter across the workpiece or radius (distance
from centre to tool tip).

This is not a setting that changes scale behaviour. It is a declaration
of how you have set up and zeroed your DRO.

Diameter Mode (ON)
------------------

The scale reads the full diameter of the material (both sides). For
example, zeroing with the tool touching the outside of a 20 mm shaft
gives a reading of 20 mm.

When this mode is active, the auto-calculated thread cutting depth is
doubled — because reducing the diameter by the full thread depth
requires removing that depth from both sides of the workpiece.

Radius Mode (OFF)
-----------------

The scale reads radius — the distance from the centre of rotation to
the tool tip. This is the more common DRO convention for lathes. A
thread depth of 0.9 mm means the tool moves 0.9 mm inward.

Which to Choose
---------------

Set this to match however your cross-slide DRO is zeroed:

- **Touching outer surface → reading = diameter** → enable Diameter Mode
- **Touching outer surface → reading = radius (half diameter)** → leave OFF

Notes
-----

- This setting only affects the automatically calculated thread depth
  shown in the wizard; it does not affect encoder or position readings
- If your finished threads are consistently too shallow or too deep by
  a factor of 2, check that this setting matches your scale configuration
