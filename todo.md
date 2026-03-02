# RCP Project Review - Findings and Recommended Actions

## Critical Issues

### 1. Security: Shell Injection in Update Screen
- **File:** `rcp/components/screens/update_screen.py:90`
- **Issue:** `subprocess.Popen(c, shell=True)` with user-selected release tag names. A crafted tag name could execute arbitrary commands.
- **Action:** Use `subprocess.Popen(c.split(), shell=False)` or `shlex.split()`, and validate tag format before use.

---

## Architecture

### 3. God Object: MainApp
- **File:** `rcp/app.py`
- **Issue:** `MainApp` holds all configuration, all device references, connection management, UI state, formatting, servo/scale lists, and update scheduling. Every component imports and references `MainApp` via `App.get_running_app()`.
- **Action:** Extract responsibilities into dedicated managers/services:
  - Connection/device management -> dedicated service (the `Board` dispatcher in `board.py` is a start)
  - Formatting/display -> `FormatsDispatcher` (already exists, but still accessed through app)
  - Configuration -> config service
  - Reduce direct `app.` references in components by passing dependencies explicitly

### 4. Dual Architecture in board.py
- **File:** `rcp/dispatchers/board.py`
- **Issue:** Contains a complete parallel architecture (`Board`, `Scale`, `Servo`, `FastData`, `Status`, `ConnectionSettings`) that duplicates the current `MainApp` + `ConnectionManager` approach. This WIP refactor creates confusion about the intended direction.
- **Action:** Decide on one approach and complete the migration, or remove the unused code. The `Board` dispatcher approach is cleaner but needs to be fully adopted.

### 5. Circular Import Dependencies
- **Issue:** Nearly every component has `from rcp.app import MainApp` inside `__init__` methods to avoid circular imports. `communication.py:31` also has a deferred import of `devices`.
- **Action:** This is a symptom of the god-object pattern. Resolving #3 would allow clean top-level imports. In the meantime, consider using dependency injection instead of `get_running_app()`.

### 6. Communication Layer Functions Should Be Methods
- **File:** `rcp/utils/communication.py`
- **Issue:** `read_float`, `write_float`, `read_long`, `write_long`, etc. are module-level functions that take `ConnectionManager` as the first argument. They all duplicate the same try/except/connected pattern.
- **Action:** Refactor as methods on `ConnectionManager`, and extract the shared try/except pattern into a decorator or helper.

### 7. Duplicated C Typedef Parsing Logic
- **File:** `rcp/utils/base_device.py`
- **Issue:** `register_type()` (classmethod) and `parse_addresses_from_definition()` (instance method) contain nearly identical C struct parsing logic, duplicated.
- **Action:** Extract shared parsing into a single function that both methods call.

---

## Dead Code and Cleanup

### 8. Dead/Commented-Out Code
- `rcp/app.py:88-91` - `beep()` method is fully commented out (no-op)
- `rcp/components/toolbars/toolbar_button.py:15-25` - class is mostly commented out
- `rcp/components/screens/home_screen.py:42-46` - `coord_bars` list created empty, assigned to `self.scales`, never used
- `rcp/components/screens/color_picker_screen.py:18-22` - commented-out `__init__`
- `rcp/components/home/home_toolbar.py:26-27` - commented-out `popup_scene`
- `rcp/components/screens/home_screen.py:93` - `TraceOutput` opens file but never closes it (resource leak)
- **Action:** Remove dead code. Either restore `beep()` or remove it entirely.

### 9. Double Assignment Bug
- **File:** `rcp/components/home/servobar.py:146`
- **Issue:** `self.index = self.index = 0` is a double assignment (harmless but looks like a typo).
- **Action:** Change to `self.index = 0`.

---

## Testing

### 10. No Test Suite
- **Issue:** Despite `pytest` being a dependency, there are zero test files. The utils layer (communication, base_device, devices, ctype_calc), dispatchers, and feeds module are all highly testable.
- **Action:** Add tests starting with:
  1. `rcp/utils/ctype_calc.py` - pure function, easiest to test
  2. `rcp/feeds.py` - data validation
  3. `rcp/utils/devices.py` - type definitions
  4. `rcp/utils/base_device.py` - C typedef parsing
  5. `rcp/dispatchers/saving_dispatcher.py` - serialization
  6. `rcp/dispatchers/circle_pattern.py` - math calculations

---

## Performance

### 11. Linear Search in BaseDevice.__getitem__
- **File:** `rcp/utils/base_device.py:40-41`
- **Issue:** `[item for item in self.variables if item.name == key][0]` does a linear scan on every property access. This is called frequently in the 30fps update loop.
- **Action:** Add a `dict` index mapping variable names to `VariableDefinition` objects, built once in `parse_addresses_from_definition()`.

### 12. Redundant Device Writes from Multiple Bindings
- **File:** `rcp/components/home/coordbar.py:83-84`
- **Issue:** `syncRatioDen` and `syncRatioNum` both bind to `set_sync_ratio`, so changing both values triggers two writes to the device when only one is needed.
- **Action:** Debounce the sync ratio update, or batch the writes.

### 13. Separate Speed Polling Loop
- **File:** `rcp/components/home/coordbar.py:86`
- **Issue:** `speed_task` runs at 25fps independently from the main 30fps `update_tick` loop. This creates unnecessary overhead and potential race conditions with `fast_data_values`.
- **Action:** Consolidate speed calculation into the main `update_tick` handler.

### 14. No Save Debouncing
- **File:** `rcp/dispatchers/saving_dispatcher.py:68-72`
- **Issue:** Every property change triggers an immediate file write via `save_settings()`. Changing multiple properties in rapid succession writes the file multiple times.
- **Action:** Add a debounce mechanism (e.g., `Clock.schedule_once` with a short delay).

---

## Priority Order

| Priority | Items | Effort |
|----------|-------|--------|
| P0 - Fix Now | #9 (double assign) | Low |
| P1 - Security | #1 (shell injection) | Low-Medium |
| P2 - Consistency | #2 (exceptions) | Medium |
| P2 - Cleanup | #8 (dead code) | Low |
| P3 - Architecture | #3 (god object), #4 (dual arch), #5 (circular imports), #6 (comm methods), #7 (parser duplication) | High |
| P3 - Performance | #11 (linear search), #12 (redundant writes), #13 (speed loop), #14 (save debouncing) | Medium |
| P4 - Quality | #10 (tests) | High |