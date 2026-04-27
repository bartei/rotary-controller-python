Thread Pitch
============

The pitch of the thread to be cut.

In **Metric Mode** the pitch is in millimetres — the distance
between adjacent thread crests measured along the axis.

In **Imperial Mode** the pitch is in TPI (threads per inch) — the
number of complete thread crests in one inch of travel.

How It Is Used
--------------

The selected pitch determines:

1. **ELS sync ratio:** the ratio of spindle rotation to saddle
   movement, set automatically on the spindle axis
2. **Auto-calculated thread depth:** shown as the default cutting
   depth in the wizard (can be overridden)
3. **Maximum spindle RPM check:** if the pitch and spindle speed
   require more servo speed than the Threading Max Speed limit, the
   system warns you before the cut

Common Pitches
--------------

**Metric (MM)**

=====  ==================
Pitch  Typical use
=====  ==================
0.5    M3, M4 fine
0.75   M5, M6 coarse
1.0    M6 fine, M8 coarse
1.25   M8 fine, M10
1.5    M10 fine, M12
2.0    M14, M16
=====  ==================

**Imperial (TPI)**

====  =======================
TPI   Typical use
====  =======================
40    ¼-40 UNF
32    #10-32 UNF
20    ¼-20 UNC
13    ½-13 UNC
8     ¾-8 UNC
4     1½-4 UNC (coarse)
====  =======================

Notes
-----

- The full pitch list is defined in the application's feeds table
- Switch Metric Mode first to see pitches in the correct unit system
