Compound Infeed
===============

Enables angled infeed for threading — each pass shifts the thread
start position slightly forward along the Z axis instead of plunging
the tool straight radially.

How It Works
------------

In standard (radial) infeed, the tool plunges straight in and cuts
both flanks of the thread simultaneously on every pass. This is simple
but increases cutting force as depth increases.

With compound infeed active, each new pass begins at a Z start
position offset slightly toward the thread stop. The tool therefore
cuts predominantly on the **leading flank**, reducing the chip load
per pass. This is similar to using a compound slide set at the thread
half-angle.

Benefits
--------

- Reduced cutting force per pass
- Less tendency for chatter, especially on coarser pitches
- Better surface finish on the thread flanks
- Easier on tool inserts and HSS tools

Compound Offset (0–5°)
----------------------

The offset angle in degrees, subtracted from the thread half-angle to
give the actual compound infeed angle:

  **compound angle = thread half-angle − offset**

The half-angle depends on the selected Thread Type:

============  ===========  ==========================
Thread Type   Half-angle   Compound angle at 1° offset
============  ===========  ==========================
ISO Metric    30°          29°
Unified       30°          29°
Whitworth     27.5°        26.5°
ACME          14.5°        13.5°
============  ===========  ==========================

**Typical setting:** 1° works well for most materials and pitches.
Increasing the offset angles the infeed more steeply toward the
leading flank.

When to Use
-----------

- Coarse pitches (> 1.5 mm / < 17 TPI): compound infeed gives the
  greatest benefit
- Fine pitches (< 1 mm / > 25 TPI): the Z offset is very small;
  compound infeed provides little benefit and can be left OFF

Notes
-----

- If a warning appears that the compound Z shift has consumed the
  remaining thread length, reduce the cross-slide infeed depth or
  increase the thread start clearance before pressing Cut
- ACME threads have a shallow half-angle (14.5°); keep the offset
  small (1° or less) to avoid too steep an approach angle
