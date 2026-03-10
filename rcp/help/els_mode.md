ELS Mode
========

Electronic Lead Screw (ELS) mode synchronizes the servo motor to
a spindle encoder, enabling electronic threading and feeding on
a manual lathe.

## Behavior

- **OFF (default):** The servo operates in positioning mode — it
  moves to commanded positions (goto, jog, sync ratio).
- **ON:** The servo locks to the spindle encoder and follows it at
  a ratio determined by the selected feed/thread pitch. The gearing
  ratios and units-per-turn settings are overridden by the ELS
  configuration.

## When to Enable

- You have a spindle encoder installed and configured
- You want to cut threads or use power feed synchronized to the
  spindle
- You have configured the lead screw pitch parameters (see below)

## Requirements

- A spindle axis must be configured and assigned in ELS Setup
- The lead screw pitch must be correctly set for your machine
- At least one saddle (Z) or cross slide (X) axis must be assigned

## Notes

- Enabling ELS mode disables the gearing ratio and units-per-turn
  fields on this screen (they are controlled by the ELS system)
- The ELS axis assignments are configured in the ELS Setup screen
- Feed and thread selections are made from the home screen toolbar