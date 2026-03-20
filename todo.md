# RCP Project Review - Findings and Recommended Actions


## Resolved

### ~~10. No Test Suite~~ RESOLVED (partially)
- Test suite now has 142 tests across 9 files:
  - `tests/dispatchers/test_board.py`
  - `tests/dispatchers/test_saving_dispatcher.py`
  - `tests/dispatchers/test_scale_dispatcher.py`
  - `tests/dispatchers/test_servo_dispatcher.py`
  - `tests/plot/test_at_position.py`
  - `tests/screens/test_update_screen.py`
  - `tests/test_kv_loader.py`
  - `tests/test_kv_syntax.py`
  - `tests/utils/test_platform.py`
- Still missing test coverage for: `utils/ctype_calc.py`, `feeds.py`, `utils/base_device.py`, `utils/devices.py`, `dispatchers/circle_pattern.py`, `dispatchers/line_pattern.py`, `dispatchers/rect_pattern.py`

---

## Refactoring

### REFACTOR-1. Redesign Input/Axis Architecture
- **Files:** `rcp/dispatchers/scale.py`, `rcp/dispatchers/axis.py`, `rcp/dispatchers/axis_transform.py`
- **Issue:** The current split between ScaleDispatcher and AxisDispatcher is convoluted. ScaleDispatcher mixes raw encoder tracking with scaling, offsets, and formatting. AxisDispatcher then re-implements its own offset system on top, leading to double-offset bugs and tangled position-setting logic. The basePosition/scaledPosition distinction is a band-aid. Sync ratio computation is duplicated across both layers.
- **Plan:**
  1. Create a clean **InputDispatcher** that owns: raw encoder position tracking, ratio (ratioNum/ratioDen), unit scaling (formats.factor), and computes a single scaled value — no offsets, no formatting.
  2. **AxisDispatcher** becomes the sole owner of: offsets, position formatting, sync ratio, spindle mode, speed display. It reads from one or more InputDispatchers via AxisTransform (identity or sum).
  3. Remove ScaleDispatcher or reduce it to a thin backward-compat wrapper.
  4. Rewrite tests for the new layering.
- **Benefit:** Single source of truth for offsets, no double-counting, simpler position-set logic, clearer separation of concerns.

---

## Architecture

### 5. Circular Import Dependencies
- **Issue:** Components still use `from rcp.app import MainApp` inside `__init__` methods to avoid circular imports. This is a known/accepted pattern documented in CLAUDE.md.
- **Action:** Consider dependency injection instead of `get_running_app()` as the codebase evolves.

### 6. Communication Layer Functions Should Be Methods
- **File:** `rcp/utils/communication.py`
- **Issue:** `read_float`, `write_float`, `read_long`, `write_long`, `read_unsigned`, `write_unsigned`, `read_signed`, `write_signed` are all module-level functions that take `ConnectionManager` as the first argument. They duplicate the same try/except/connected pattern.
- **Action:** Refactor as methods on `ConnectionManager`, and extract the shared try/except pattern into a decorator or helper.

### 7. Duplicated C Typedef Parsing Logic
- **File:** `rcp/utils/base_device.py`
- **Issue:** `register_type()` (classmethod) and `parse_addresses_from_definition()` (instance method) contain nearly identical C struct parsing logic.
- **Action:** Extract shared parsing into a single function that both methods call.

---

## Dead Code and Cleanup

### 8. Dead/Commented-Out Code
- `rcp/app.py:56-59` - `beep()` method is a no-op with commented-out implementation
- `rcp/components/toolbars/toolbar_button.py:12-22` - class body is `pass` followed by commented-out code
- `rcp/components/screens/color_picker_screen.py:15-19` - commented-out `__init__`
- `rcp/components/home/home_toolbar.py:20-21` - commented-out `popup_scene`
- `rcp/components/screens/home_screen.py` - `TraceOutput` opens file but `self.exit_stack` is never initialized (would raise `AttributeError` at runtime)
- **Action:** Remove dead code. Either restore `beep()` or remove it entirely. Fix or remove the `TraceOutput` code path.

---

## Performance (profiled on RPi3 — 5.7s capture)

### PERF-7. Redundant property writes in ServoDispatcher
- **File:** `rcp/dispatchers/servo.py`
- **Issue:** `on_update_tick()` writes `self.servoEnable` and `self.speed` every tick even when unchanged. Each triggers Kivy property dispatch chain.
- **Action:** Compare before writing.

### PERF-8. Duplicate factor bindings
- **Files:** `rcp/dispatchers/scale.py`, `rcp/dispatchers/axis.py`
- **Issue:** Both bind `formats.factor` to two separate callbacks. A single factor change fires both.
- **Action:** Bind to one handler that calls both.

### PERF-10. Separate Speed Polling Loop
- **File:** `rcp/dispatchers/scale.py:76`
- **Issue:** `speed_task` runs at 25fps via its own `Clock.schedule_interval`, independently from the main `update_tick` loop. Creates unnecessary overhead.
- **Action:** Consolidate speed calculation into the main `update_tick` handler.

### PERF-11. Identity transform fast path
- **File:** `rcp/dispatchers/axis.py`
- **Issue:** `_update_position()` allocates a dict every tick, even for identity transforms (single scale, weight=1).
- **Action:** Short-circuit for single-contribution transforms.

---

## Test Coverage Gaps

### 15. Remaining Untested Modules
- **Priority areas still lacking tests:**
  1. `rcp/utils/ctype_calc.py` - pure functions, easiest to test
  2. `rcp/feeds.py` - data validation
  3. `rcp/utils/base_device.py` - C typedef parsing
  4. `rcp/utils/devices.py` - type definitions
  5. `rcp/dispatchers/circle_pattern.py` - math calculations
  6. `rcp/dispatchers/line_pattern.py` - math calculations
  7. `rcp/dispatchers/rect_pattern.py` - math calculations

---

## Priority Order

| Priority | Items | Effort | Impact |
|----------|-------|--------|--------|
| ~~P0 - Performance~~ | ~~PERF-1 (scene rebuild — 39% CPU)~~ | ~~Low~~ | ~~Critical~~ |
| ~~P0 - Performance~~ | ~~PERF-2 (coords overlay visibility)~~ | ~~Low~~ | ~~High~~ |
| P1 - Performance | PERF-3 (BaseDevice cache) | Low | Medium |
| P1 - Performance | PERF-4 (text rendering guards) | Low | Medium |
| P1 - Performance | PERF-5 (Fraction caching) | Medium | Medium |
| P2 - Performance | PERF-6 (save debouncing) | Low | Medium |
| P2 - Performance | PERF-7 to PERF-11 (misc) | Medium | Low-Medium |
| **P0 - Refactor** | **REFACTOR-1 (Input/Axis redesign)** | **High** | **Critical** |
| P1 - Cleanup | #8 (dead code, TraceOutput bug) | Low | - |
| P3 - Architecture | #5, #6, #7 | High | - |
| P4 - Quality | #15 (test coverage gaps) | Medium | - |
