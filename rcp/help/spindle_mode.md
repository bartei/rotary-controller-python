Spindle Mode
============

When enabled, this axis is treated as a spindle (rotational speed
source) rather than a positional axis.

## Behavior

- **OFF (default):** The axis displays position values (mm, inches,
  or degrees) and supports sync/goto operations.
- **ON:** The axis displays rotational speed (RPM) instead of position.
  This is used for spindle encoders on lathes or milling machines.

## When to Enable

- The axis is connected to a spindle encoder
- You want to display RPM on the home screen
- You are using ELS (Electronic Lead Screw) mode and need a spindle
  reference signal

## Notes

- A spindle-mode axis can still be assigned as the ELS spindle source
  in the ELS Setup screen
- Only one axis typically needs spindle mode enabled
- Enabling spindle mode changes the display format to use the RPM
  format settings from the Formats screen