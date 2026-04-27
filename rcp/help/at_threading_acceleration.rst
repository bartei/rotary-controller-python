Threading Acceleration (Steps/s²)
==================================

How quickly the servo ramps up to threading speed at the start of
each cut, and decelerates to a stop at the thread end.

How It Works
------------

The servo uses a trapezoidal motion profile during the threading cut:

1. Accelerate at this rate from rest up to the threading max speed
2. Cruise at threading max speed for the length of the thread
3. Decelerate at this rate to stop at the end position

A higher acceleration reaches full cutting speed sooner, which is
important for short threads where a slow ramp-up would consume most
of the thread length before the servo is up to speed.

Guidelines
----------

- Higher values: faster ramp-up, shorter effective lead-in — better
  for short threads
- Lower values: gentler start, less mechanical stress — better for
  heavy setups with large inertia
- Too high with a heavy load: risk of missed steps during the ramp

Typical Range
-------------

**Typical starting point:** approximately 2× your Threading Max Speed
value (e.g., max speed 1000 steps/s → acceleration 2000 steps/s²).

Increase gradually until the ramp feels responsive without causing
missed steps.

Notes
-----

- Value must be a positive integer
- The same rate is used for both accelerating and decelerating
- For general servo acceleration guidance see the Servo Acceleration
  help (servo_acceleration.md) in the Servo setup screen
