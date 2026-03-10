Weight Numerator / Denominator
===============================

The weight ratio is a multiplier applied to a scale input within
a Scaling or Weighted Sum transform.

    weighted_value = scale_input × (Weight Numerator / Weight Denominator)

## When Used

- **Scaling transform:** A single weight ratio is applied to the
  primary scale input.
- **Weighted Sum transform:** Each of the two scale inputs has its
  own independent weight ratio.

## Examples

| Scenario                 | Num | Den | Effect              |
|--------------------------|-----|-----|---------------------|
| Pass-through (no change) | 1   | 1   | 1:1 ratio           |
| Halve the reading        | 1   | 2   | 0.5× multiplier     |
| Gear ratio 1:72          | 1   | 72  | Divide by 72        |

## Notes

- Both values must be positive integers
- The weight is applied after the scale ratio conversion
- Click "Apply Transform" to save changes