Transform Type
==============

Defines how raw scale input(s) are converted into this axis's
displayed value. Each transform type applies a different formula.

## Available Types

### Identity
Passes the scale input through with no modification.

    axis_value = scale_input

Use this for simple single-scale axes (most common).

### Scaling
Multiplies the scale input by a weight ratio.

    axis_value = scale_input × (Weight Num / Weight Den)

Use this to apply a gear ratio or unit conversion on top of the
scale ratio.

### Weighted Sum
Combines two scale inputs with independent weights.

    axis_value = (input_0 × W0_Num/W0_Den) + (input_1 × W1_Num/W1_Den)

Use this for compound axis calculations (e.g., summing two linear
encoders, or computing a derived measurement from two inputs).

### Angle Cos
Computes the cosine projection of a scale input at a fixed angle.

    axis_value = scale_input × cos(angle)

Use this for angled linear scales (e.g., computing the X component
of a compound slide at a known angle).

### Angle Sin
Computes the sine projection of a scale input at a fixed angle.

    axis_value = scale_input × sin(angle)

Use this for computing the Y component of an angled axis.

## Notes

- Changing the transform type shows/hides the relevant parameter
  fields below it
- You must click "Apply Transform" at the bottom of the screen to
  save changes