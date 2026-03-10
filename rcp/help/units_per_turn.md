Units Per Turn
==============

The number of display units that correspond to one full revolution
of the output axis (after gearing). The default is 360, representing
degrees.

## Common Values

| Application           | Units per Turn | Meaning               |
|-----------------------|----------------|-----------------------|
| Rotary table (degrees)| 360            | 360° per revolution   |
| Rotary table (grads)  | 400            | 400 grads per rev     |
| Dividing (divisions)  | N              | N equal divisions     |

## How It Works

This value tells the DRO how to interpret one full rotation of the
output shaft. Combined with the gearing ratio, it determines the
relationship between motor steps and displayed position.

## Examples

**Standard rotary table:**
Set to 360. The DRO displays position in degrees (0–360).

**100-division indexing:**
Set to 100. The DRO displays position as division numbers (0–100),
where each unit represents 3.6° of physical rotation.

## Notes

- Must be a positive integer
- This setting is disabled when ELS mode is active
- Changing this value affects how positions are displayed but does
  not change the physical motion