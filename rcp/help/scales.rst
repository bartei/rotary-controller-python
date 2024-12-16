Scales Ratio Configuration
==========================
The DRO internals work with a 1um resolution.
Depending on the type of scale you connected to the DRO, a suitable
conversion factor has to be configured. Here are some examples:

- 1um scale: num=1, den=1
- 5um scale: num=5, den=1
- 0.001" scale: num=1000, den=254