Acceleration (Steps/s²)
=======================

How quickly the motor ramps up to maximum speed, expressed in
steps per second squared.

## How It Works

The servo uses a trapezoidal motion profile:
1. Accelerate at this rate until reaching max speed
2. Cruise at max speed
3. Decelerate at this rate to stop at the target

## Guidelines

- Higher values = snappier response but more stress on the
  mechanical system
- Lower values = smoother motion but slower overall moves
- Start conservative and increase until you find the sweet spot

## Typical Ranges

| Setup                 | Typical Acceleration  |
|-----------------------|-----------------------|
| Light rotary table    | 500–2000 steps/s²     |
| Heavy rotary table    | 200–1000 steps/s²     |
| Lathe carriage        | 1000–5000 steps/s²    |

## Notes

- Value must be a positive integer
- Too high acceleration with heavy loads causes missed steps
- Too low acceleration makes the system feel sluggish
- The same acceleration value is used for both speeding up and
  slowing down