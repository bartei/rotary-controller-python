# RCP Project Review - Findings and Recommended Actions

*Last updated: 2026-03-01*

## Resolved

### ~~3. God Object: MainApp~~ RESOLVED
- `MainApp` has been significantly refactored (~107 lines). `Board`, `ServoDispatcher`, and `ScaleDispatcher` have been extracted to their own modules. `MainApp` now only holds top-level wiring and backward-compat aliases.

### ~~4. Dual Architecture in board.py~~ RESOLVED
- `rcp/dispatchers/board.py` now contains a single clean `Board` class (~84 lines) that owns `ConnectionManager`, one `ServoDispatcher`, and four `ScaleDispatcher` instances.

### ~~9. Double Assignment Bug~~ RESOLVED
- Logic moved to `ServoDispatcher`; the double assignment is gone. `self.index = 0` in `update_positions()`.

### ~~8c. coord_bars unused~~ RESOLVED
- `coord_bars` in `home_screen.py` is now populated and used to hold `CoordBar` widget references.

### ~~10. No Test Suite~~ RESOLVED (partially)
- Test suite now has 101 tests across multiple files:
  - `tests/dispatchers/test_board.py`
  - `tests/dispatchers/test_saving_dispatcher.py`
  - `tests/dispatchers/test_scale_dispatcher.py`
  - `tests/dispatchers/test_servo_dispatcher.py`
  - `tests/plot/test_at_position.py`
  - `tests/test_kv_loader.py`
  - `tests/test_kv_syntax.py`
- Still missing test coverage for: `utils/ctype_calc.py`, `feeds.py`, `utils/base_device.py`, `utils/devices.py`, `dispatchers/circle_pattern.py`

---

## Critical Issues

### 1. Security: Shell Injection in Update Screen
- **File:** `rcp/components/screens/update_screen.py:88`
- **Issue:** `subprocess.Popen(c, shell=True)` with user-selected release tag names. A crafted tag name could execute arbitrary commands.
- **Action:** Use `subprocess.Popen(shlex.split(c), shell=False)` and validate tag format before use.

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

## Performance

### 11. Linear Search in BaseDevice.__getitem__ / __setitem__
- **File:** `rcp/utils/base_device.py:41-44, 57-59`
- **Issue:** Both `__getitem__` and `__setitem__` use `[item for item in self.variables if item.name == key][0]` — O(n) linear scan on every property access. Called frequently in the 30fps update loop.
- **Action:** Add a `dict` index mapping variable names to `VariableDefinition` objects, built once in `parse_addresses_from_definition()`.

### 12. Redundant Device Writes from Multiple Bindings
- **File:** `rcp/dispatchers/scale.py:73-74, 126-129`
- **Issue:** `syncRatioDen` and `syncRatioNum` each trigger `set_sync_ratio` twice per change — once via `self.bind()` and once via `on_syncRatioNum`/`on_syncRatioDen` handlers. Writing to the device also re-triggers these callbacks.
- **Action:** Remove the duplicate bindings (keep either `bind()` or `on_*` handlers, not both). Add debouncing or guard against re-entrant calls.

### 13. Separate Speed Polling Loop
- **File:** `rcp/dispatchers/scale.py:76`
- **Issue:** `speed_task` runs at 25fps via its own `Clock.schedule_interval`, independently from the main `update_tick` loop. Creates unnecessary overhead.
- **Action:** Consolidate speed calculation into the main `update_tick` handler.

### 14. No Save Debouncing
- **File:** `rcp/dispatchers/saving_dispatcher.py:69-85`
- **Issue:** Every property change triggers an immediate synchronous file write via `save_settings()`. Changing multiple properties in rapid succession writes the file multiple times.
- **Action:** Add a debounce mechanism (e.g., `Clock.schedule_once` with a short delay).

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

| Priority | Items | Effort |
|----------|-------|--------|
| P1 - Security | #1 (shell injection) | Low-Medium |
| P2 - Cleanup | #8 (dead code, TraceOutput bug) | Low |
| P3 - Architecture | #5 (circular imports), #6 (comm methods), #7 (parser duplication) | High |
| P3 - Performance | #11 (linear search), #12 (redundant writes), #13 (speed loop), #14 (save debouncing) | Medium |
| P4 - Quality | #15 (test coverage gaps) | Medium |
