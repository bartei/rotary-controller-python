Angle (degrees)
================

The fixed angle used by the Angle Cos and Angle Sin transforms.

    Angle Cos: axis_value = scale_input × cos(angle)
    Angle Sin: axis_value = scale_input × sin(angle)

## Typical Use

On a lathe with a compound slide set at an angle, a single linear
encoder on the compound measures travel along the slide. To display
the X and Z components separately:

1. Create an axis with **Angle Cos** transform → shows the
   longitudinal (Z) component
2. Create another axis with **Angle Sin** transform → shows the
   cross (X) component

## Example

Compound slide set at 29.5°:
- Set Angle = 29.5
- Cos axis shows: compound_travel × cos(29.5°) ≈ 0.870 × travel
- Sin axis shows: compound_travel × sin(29.5°) ≈ 0.492 × travel

## Notes

- The angle is specified in degrees (not radians)
- Accepts decimal values (e.g., 29.5, 45.0, 60.25)
- Click "Apply Transform" to save changes