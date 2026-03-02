from kivy.properties import NumericProperty, StringProperty

from rcp.dispatchers.saving_dispatcher import SavingDispatcher


class PlainDispatcher(SavingDispatcher):
    value = NumericProperty(42)
    label = StringProperty("hello")

    _skip_save = []


class OverriddenDispatcher(SavingDispatcher):
    _save_class_name = "LegacyName"
    value = NumericProperty(99)

    _skip_save = []


class TestSavingDispatcherFilename:
    def test_default_uses_class_name(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        d = PlainDispatcher(id_override="0")
        assert d.filename.name == "PlainDispatcher-0.yaml"

    def test_save_class_name_overrides_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        d = OverriddenDispatcher(id_override="0")
        assert d.filename.name == "LegacyName-0.yaml"

    def test_round_trip_with_override(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        # Write with one class name
        d1 = OverriddenDispatcher(id_override="1")
        d1.value = 123
        d1.save_settings()

        # Read back with a fresh instance
        d2 = OverriddenDispatcher(id_override="1")
        assert d2.value == 123

    def test_different_overrides_use_different_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        d1 = OverriddenDispatcher(id_override="0")
        d2 = PlainDispatcher(id_override="0")
        assert d1.filename.name != d2.filename.name
