Scale Input
===========

Selects which hardware scale input feeds data into this axis.

## How It Works

The DRO hardware has multiple scale input channels (Input 0, Input 1,
etc.). Each channel reads from a physical encoder connected to the
board. This dropdown maps a hardware input to this axis.

## Multiple Axes, Same Input

Multiple axes can read from the same physical input. For example:
- An "X" axis using Input 0 with identity transform
- A "Compound X" axis using Input 0 with an Angle Cos transform

This lets you derive multiple logical axes from a single encoder.

## Sync Conflict

If two axes share the same physical scale input, they cannot both
have sync mode enabled at the same time. The system will warn you
if a conflict is detected.

## Notes

- The dropdown lists all configured scale inputs by index
- If no inputs are configured, set them up in the Inputs screen first