Scale Ratio Configuration
=========================

Each scale input reads raw encoder counts. The ratio converts these
counts into millimeters for display:

    position_mm = raw_counts × (Numerator / Denominator)

## Common Scale Configurations

| Scale Type       | Resolution | Numerator | Denominator |
|------------------|------------|-----------|-------------|
| 1 µm linear      | 0.001 mm   | 1         | 1000        |
| 5 µm linear      | 0.005 mm   | 1         | 200         |
| 0.5 µm linear    | 0.0005 mm  | 1         | 2000        |
| 0.001" encoder   | 0.0254 mm  | 127       | 5000        |

## Examples

**1 µm glass scale:**
Each tick = 0.001 mm. Set Numerator=1, Denominator=1000.

**5 µm glass scale:**
Each tick = 0.005 mm. Set Numerator=1, Denominator=200.

**0.001" (1 mil) scale:**
Each tick = 0.0254 mm = 127/5000. Set Numerator=127, Denominator=5000.

## Tips

- Both values must be positive integers
- If your DRO readings are exactly half or double the expected value,
  your ratio is likely off by a factor of 2
- Check your scale's datasheet for the exact resolution per count