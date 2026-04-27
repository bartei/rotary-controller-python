"""
Shared pytest configuration.

Installs lightweight stubs into sys.modules before any test module imports
code that depends on Kivy.  This lets pure-logic unit tests run without a
display or the full Kivy runtime.

Strategy
--------
* Stub only *specific* submodules (e.g. ``kivy.logger``), never the top-level
  ``kivy`` package itself.  Replacing ``sys.modules["kivy"]`` with a plain
  ModuleType makes it "not a package", which prevents *all* kivy submodule
  imports and breaks tests that need real Kivy (dispatchers, screens, etc.).
* Stub ``rcp.*`` modules whose import chains would otherwise drag in Kivy UI
  classes (boxlayout, popup, etc.) that require a display or OpenGL.
* Leave ``rcp.utils.devices`` un-stubbed: it only uses kivy.logger (stubbed
  above) and is safe to import headlessly.
"""

import sys
import types
from unittest.mock import MagicMock


def _install_kivy_stubs() -> None:
    """Populate sys.modules with minimal stubs."""

    def _mock_module(name: str, **attrs) -> types.ModuleType:
        mod = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(mod, k, v)
        sys.modules[name] = mod
        return mod

    # kivy.logger — used by every rcp module for Logger.getChild(...)
    # Stub the submodule directly; do NOT replace sys.modules["kivy"] itself
    # (that would make kivy "not a package" and break dispatcher/screen tests).
    mock_logger = MagicMock()
    mock_logger.getChild.side_effect = lambda name: MagicMock()
    _mock_module(
        "kivy.logger",
        Logger=mock_logger,
        LOG_LEVELS={},
        logger_config_update=MagicMock(),
        file_log_handler=MagicMock(),
    )

    # rcp.components.widgets.custom_popup — stubbing the whole module prevents
    # its import chain (kivy.properties, kivy.uix.*) from running, which
    # would fail without a display.
    _mock_module(
        "rcp.components.widgets.custom_popup",
        CustomPopup=MagicMock(),
    )


_install_kivy_stubs()
