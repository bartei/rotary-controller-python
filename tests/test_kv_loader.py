from unittest.mock import patch

from rcp.utils.kv_loader import load_kv, get_loaded_kv_files, _loaded_kv_files


class TestLoadKv:
    def setup_method(self):
        """Clear the loaded files registry before each test."""
        _loaded_kv_files.clear()

    def test_loads_existing_kv_file(self, tmp_path):
        """load_kv should load a .kv file that exists alongside the .py file."""
        py_file = str(tmp_path / "widget.py")
        kv_file = str(tmp_path / "widget.kv")

        with open(kv_file, "w") as f:
            f.write("<Widget>:\n    pass\n")

        with patch("rcp.utils.kv_loader.Builder") as mock_builder:
            result = load_kv(py_file)

        assert result == kv_file
        mock_builder.load_file.assert_called_once_with(kv_file)

    def test_returns_none_when_kv_missing(self, tmp_path):
        """load_kv should return None when no .kv file exists."""
        py_file = str(tmp_path / "widget.py")

        with patch("rcp.utils.kv_loader.Builder") as mock_builder:
            result = load_kv(py_file)

        assert result is None
        mock_builder.load_file.assert_not_called()

    def test_prevents_duplicate_loading(self, tmp_path):
        """load_kv should skip a .kv file that was already loaded."""
        py_file = str(tmp_path / "widget.py")
        kv_file = str(tmp_path / "widget.kv")

        with open(kv_file, "w") as f:
            f.write("<Widget>:\n    pass\n")

        with patch("rcp.utils.kv_loader.Builder") as mock_builder:
            first = load_kv(py_file)
            second = load_kv(py_file)

        assert first == kv_file
        assert second is None
        mock_builder.load_file.assert_called_once_with(kv_file)

    def test_get_loaded_kv_files_returns_copy(self, tmp_path):
        """get_loaded_kv_files should return a copy, not the internal set."""
        py_file = str(tmp_path / "widget.py")
        kv_file = str(tmp_path / "widget.kv")

        with open(kv_file, "w") as f:
            f.write("<Widget>:\n    pass\n")

        with patch("rcp.utils.kv_loader.Builder"):
            load_kv(py_file)

        loaded = get_loaded_kv_files()
        assert kv_file in loaded

        loaded.clear()
        assert len(get_loaded_kv_files()) == 1

    def test_multiple_different_files(self, tmp_path):
        """load_kv should track each file independently."""
        for name in ["alpha", "beta", "gamma"]:
            with open(tmp_path / f"{name}.kv", "w") as f:
                f.write(f"<{name}>:\n    pass\n")

        with patch("rcp.utils.kv_loader.Builder") as mock_builder:
            for name in ["alpha", "beta", "gamma"]:
                load_kv(str(tmp_path / f"{name}.py"))

        assert mock_builder.load_file.call_count == 3
        assert len(get_loaded_kv_files()) == 3