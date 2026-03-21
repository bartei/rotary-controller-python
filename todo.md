# RCP Project Review - Findings and Recommended Actions

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
