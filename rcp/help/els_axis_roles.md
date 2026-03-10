ELS Axis Roles
==============

Assigns which configured axes serve as the spindle, saddle (Z),
and cross slide (X) for Electronic Lead Screw operation.

## Axis Roles

### Spindle Axis
The rotational reference input. This axis must be connected to
a spindle encoder and should have Spindle Mode enabled.
The ELS system reads the spindle speed and position from this axis
to synchronize the servo feeds.

### Saddle Axis (Z)
The longitudinal axis — typically the carriage/saddle on a lathe.
When ELS is active, this axis follows the spindle at the selected
thread pitch or feed rate for longitudinal cuts and threading.

### Cross Slide Axis (X)
The transverse axis — typically the cross slide on a lathe.
When ELS is active, this axis can be synchronized for facing
operations or taper turning.

## Configuration

- Select axis names from the dropdowns (or "None" to leave
  unassigned)
- Each role must be assigned to a different axis
- The spindle axis must be configured before Z or X can operate
  in ELS mode

## Notes

- Axes are listed by their configured names from the Axes setup
- If no axes are configured yet, set them up in the Axes screen first
- You can leave X or Z as "None" if your setup only needs one
  synchronized axis