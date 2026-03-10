Lead Screw Pitch
================

These settings describe the physical lead screw on your lathe.
The ELS system needs this information to calculate the correct
servo speed for each thread pitch or feed rate.

## Lead Screw Pitch (in MM or IN)

The linear distance the carriage travels per revolution of the
lead screw. Set the value and unit (mm or inch) to match your
machine.

### Common Values

| Machine Type          | Pitch     | Unit  |
|-----------------------|-----------|-------|
| Metric lathe (2mm)    | 2.0       | MM    |
| Metric lathe (3mm)    | 3.0       | MM    |
| Imperial lathe (8 TPI)| 0.125     | Inch  |
| Imperial lathe (12 TPI)| 0.0833  | Inch  |

**TPI to pitch:** pitch_inches = 1 / TPI
- 8 TPI → 1/8 = 0.125"
- 12 TPI → 1/12 ≈ 0.0833"

## Pitch in Inch

Toggle whether the lead screw pitch value is in inches or
millimeters. Enable this if your lead screw is specified in TPI
or inches. Disable for metric lead screws.

## Lead Screw Pitch Steps

The number of stepper motor steps required for one full revolution
of the lead screw. This depends on your motor's step angle and
any microstepping configuration.

### Examples

| Motor         | Microstepping | Steps/Rev |
|---------------|---------------|-----------|
| 1.8° stepper  | Full step     | 200       |
| 1.8° stepper  | 1/4 step      | 800       |
| 1.8° stepper  | 1/8 step      | 1600      |
| 1.8° stepper  | 1/16 step     | 3200      |
| 0.9° stepper  | Full step     | 400       |

If there is a gear or belt reduction between the motor and lead
screw, multiply the steps by the gear ratio.

## Notes

- All three parameters must be set correctly for accurate threading
- These fields are only editable when ELS mode is enabled
- Incorrect values result in wrong thread pitches