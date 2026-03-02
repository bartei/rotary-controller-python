from unittest.mock import patch, MagicMock

import pytest

from rcp.components.screens.update_screen import UpdateScreen, DEV_RELEASE


@pytest.fixture
def screen():
    with patch.object(UpdateScreen, "schedule_refresh_releases"), \
         patch.object(UpdateScreen, "apply_class_lang_rules"):
        s = UpdateScreen()
    return s


class TestAllowExperimental:
    def test_dev_entry_added_when_enabled(self, screen):
        screen.releases = ["v1.0", "v0.9"]
        screen.allow_experimental = True
        assert DEV_RELEASE in screen.releases

    def test_dev_entry_removed_when_disabled(self, screen):
        screen.releases = ["v1.0", "v0.9"]
        screen.allow_experimental = True
        assert DEV_RELEASE in screen.releases

        screen.allow_experimental = False
        assert DEV_RELEASE not in screen.releases

    def test_official_releases_preserved_when_toggled(self, screen):
        screen.releases = ["v1.0", "v0.9"]
        screen.allow_experimental = True
        screen.allow_experimental = False
        assert screen.releases == ["v1.0", "v0.9"]

    def test_dev_entry_not_duplicated_on_repeated_enable(self, screen):
        screen.releases = ["v1.0"]
        screen.allow_experimental = True
        screen.allow_experimental = True
        assert screen.releases.count(DEV_RELEASE) == 1

    def test_selected_release_reset_when_dev_disabled(self, screen):
        screen.releases = ["v1.0", "v0.9"]
        screen.allow_experimental = True
        screen.selected_release = DEV_RELEASE

        screen.allow_experimental = False
        assert screen.selected_release != DEV_RELEASE
        assert screen.selected_release == "v1.0"

    def test_selected_release_unchanged_when_not_dev(self, screen):
        screen.releases = ["v1.0", "v0.9"]
        screen.selected_release = "v0.9"
        screen.allow_experimental = True
        screen.allow_experimental = False
        assert screen.selected_release == "v0.9"


class TestSetReleases:
    def test_includes_dev_when_experimental_enabled(self, screen):
        screen.allow_experimental = True
        screen._set_releases(["v2.0", "v1.9"])
        assert screen.releases == ["v2.0", "v1.9", DEV_RELEASE]

    def test_excludes_dev_when_experimental_disabled(self, screen):
        screen.allow_experimental = False
        screen._set_releases(["v2.0", "v1.9"])
        assert screen.releases == ["v2.0", "v1.9"]

    def test_refresh_preserves_dev_entry(self, screen):
        """Simulates a refresh when experimental is already enabled."""
        screen.allow_experimental = True
        # Simulate what refresh_releases does internally
        screen._set_releases(["v3.0", "v2.9"])
        assert DEV_RELEASE in screen.releases
        assert "v3.0" in screen.releases


class TestInstallRelease:
    def test_normal_release_calls_do_install_directly(self, screen):
        screen.selected_release = "v1.0"
        with patch.object(screen, "_do_install") as mock_install, \
             patch.object(screen, "_confirm_dev_install") as mock_confirm:
            screen.install_release()
            mock_install.assert_called_once()
            mock_confirm.assert_not_called()

    def test_dev_release_calls_confirm_dialog(self, screen):
        screen.selected_release = DEV_RELEASE
        with patch.object(screen, "_do_install") as mock_install, \
             patch.object(screen, "_confirm_dev_install") as mock_confirm:
            screen.install_release()
            mock_confirm.assert_called_once()
            mock_install.assert_not_called()
