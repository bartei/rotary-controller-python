Display Format Digits
=====================

Controls how many decimal places are shown for position and speed
values on the DRO display.

## Settings

### Metric Position Digits
Decimal places for position values in millimeter mode.
- Default: 3 (shows ±123.456 mm)
- Range: 0–6

### Metric Speed Digits
Decimal places for speed values in millimeter mode (mm/min).
- Default: 1 (shows ±123.4 mm/min)

### Imperial Position Digits
Decimal places for position values in inch mode.
- Default: 4 (shows ±1.2345")
- Common: 4 for standard machining, 5 for precision work

### Imperial Speed Digits
Decimal places for speed values in inch mode (in/min).
- Default: 3

### Angle Format Digits
Decimal places for angular position values (degrees).
- Default: 2 (shows ±123.45°)

### Angle Speed (RPM) Format Digits
Decimal places for rotational speed values (RPM).
- Default: 0 (shows whole RPM numbers like 1200 RPM)

## Notes

- All values must be positive integers
- More digits = more precision displayed, but the actual resolution
  is limited by your scale hardware
- Very high digit counts may cause display overflow on small screens