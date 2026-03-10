Maximum Speed (Steps/s)
=======================

The maximum velocity the stepper/servo motor is allowed to reach,
expressed in steps per second.

## Guidelines

- Start with a conservative value and increase gradually
- Exceeding your motor's capability causes missed steps and
  position errors
- The actual speed depends on your motor, driver, and power supply

## Typical Ranges

| Motor Type            | Typical Max Speed     |
|-----------------------|-----------------------|
| NEMA 17 stepper       | 1000–3000 steps/s     |
| NEMA 23 stepper       | 500–2000 steps/s      |
| NEMA 34 stepper       | 300–1500 steps/s      |
| Closed-loop servo     | 2000–10000 steps/s    |

These are rough guidelines — actual values depend on microstepping
settings, supply voltage, and load.

## Notes

- Value must be a positive integer
- The motor accelerates up to this speed (see Acceleration setting)
  and never exceeds it
- If you hear grinding or the motor stalls during fast moves,
  reduce this value