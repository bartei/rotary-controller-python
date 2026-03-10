Position Tolerance (mm)
=======================

The acceptable position error threshold, in millimeters. When the
current position is within this distance of a target, the DRO
considers the axis to be "at position."

## How It Works

During a servo goto operation, the position indicator changes
color (or shows a confirmation) when the actual position is within
the tolerance of the commanded target.

## Typical Values

| Application           | Tolerance   |
|-----------------------|-------------|
| General machining     | 0.01 mm     |
| Precision work        | 0.005 mm    |
| Rough positioning     | 0.1 mm      |
| Rotary indexing       | 0.05 mm     |

## Notes

- Value is always in millimeters regardless of the display unit
- Accepts decimal values
- Setting too tight a tolerance may cause the indicator to never
  show "at position" due to encoder noise
- Setting too loose loses the benefit of position verification