Servo Gearing Ratios
====================

The servo gearing ratio defines the relationship between stepper
motor steps and the output axis rotation in degrees.

    output_degrees = motor_steps × (Numerator / Denominator)

Numerator is typically 360 (degrees per full output revolution).
Denominator is the total number of motor steps needed for one
full revolution of the output (steps/rev × gear ratio).

## Examples

### Direct drive — 400 step motor on rotary table
No gearing between motor and table.

- Numerator = 360
- Denominator = 400
- Each step = 360/400 = 0.9°

### 90:1 worm gear — 400 step motor
Common dividing head with 90:1 worm reduction.

- Numerator = 360
- Denominator = 400 × 90 = 36000
- Each step = 360/36000 = 0.01°

### 40:1 worm gear — 200 step motor
Smaller dividing head with 200-step motor.

- Numerator = 360
- Denominator = 200 × 40 = 8000
- Each step = 360/8000 = 0.045°

### 72:1 worm gear — 200 step motor
- Numerator = 360
- Denominator = 200 × 72 = 14400
- Each step = 360/14400 = 0.025°

## How to Calculate

1. Find your motor's steps per revolution (typically 200 or 400)
2. Find the gear/worm reduction ratio of your rotary table
3. Set Numerator = 360
4. Set Denominator = steps_per_rev × gear_ratio

If using microstepping on the driver (e.g., 1/4 step), multiply
the motor steps accordingly:
- 200 step motor at 1/4 microstepping = 800 effective steps/rev
- Denominator = 800 × gear_ratio

## Notes

- Both values must be positive integers
- This setting is disabled when ELS mode is active
- If the table overshoots or undershoots commanded positions, verify
  your steps/rev and gear ratio values