Sync Ratio
==========

The sync ratio defines how many units the servo moves per unit of
movement on the reference axis when synchronized movement (sync mode)
is active.

    servo_movement = reference_movement × (Numerator / Denominator)

## Unit Normalization

The ratio works in the **display units currently selected by the
user** (millimeters or inches). This means:

- **In MM mode:** the ratio is applied per millimeter of reference
  axis movement, and the servo moves in its own configured units
  (typically degrees for a rotary table).
- **In Inch mode:** the ratio is applied per inch of reference axis
  movement.

The DRO automatically handles the unit conversion, so the same
physical behavior is maintained regardless of display mode.

## Examples

### Rotary Table (1:100 ratio)
- Numerator = 1, Denominator = 100
- For every 1 mm of travel on the reference axis, the servo
  rotates 1/100 = 0.01°
- 100 mm of travel → 1° of rotation
- Useful for very fine angular positioning driven by linear travel

### Direct 1:1
- Numerator = 1, Denominator = 1
- The servo moves 1 unit for each 1 unit of reference movement
- Example: 1 mm of reference travel → 1° of rotation

### Threading (lathe)
- Numerator = 1, Denominator = 25
- For each mm of spindle-driven travel, the carriage advances
  1/25 = 0.04 mm → producing a 0.04 mm pitch thread
- Adjust Numerator and Denominator to match the desired thread pitch

### Dividing head with 90:1 worm gear
- Numerator = 1, Denominator = 90
- The worm gear reduces motion by 90:1
- 90 units of input → 1° of table rotation

## Notes

- Both values must be positive integers
- Only axes that do not share the same physical scale input as
  another synced axis can enable sync simultaneously
- The sync ratio is applied on top of the scale ratio and axis
  transform
- Switching between MM and Inch display modes does not change the
  physical behavior — the DRO normalizes the ratio automatically