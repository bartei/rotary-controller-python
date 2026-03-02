import subprocess
from unittest.mock import patch, mock_open

from rcp.utils.platform import (
    is_raspberry_pi,
    parse_disk_and_partition,
    get_root_device,
    get_block_size_bytes,
    get_filesystem_usage,
    format_bytes,
)


class TestIsRaspberryPi:
    def test_raspberry_pi_model(self):
        data = "Raspberry Pi 4 Model B Rev 1.4\x00"
        with patch("builtins.open", mock_open(read_data=data)):
            assert is_raspberry_pi() is True

    def test_non_pi_model(self):
        data = "QEMU Virtual Machine\x00"
        with patch("builtins.open", mock_open(read_data=data)):
            assert is_raspberry_pi() is False

    def test_missing_file(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert is_raspberry_pi() is False

    def test_permission_error(self):
        with patch("builtins.open", side_effect=PermissionError):
            assert is_raspberry_pi() is False


class TestParseDiskAndPartition:
    def test_mmcblk_style(self):
        assert parse_disk_and_partition("/dev/mmcblk0p2") == ("/dev/mmcblk0", "2")

    def test_mmcblk_style_double_digit(self):
        assert parse_disk_and_partition("/dev/mmcblk1p12") == ("/dev/mmcblk1", "12")

    def test_sd_style(self):
        assert parse_disk_and_partition("/dev/sda2") == ("/dev/sda", "2")

    def test_sd_style_multi_letter(self):
        assert parse_disk_and_partition("/dev/sdab3") == ("/dev/sdab", "3")

    def test_nvme_style(self):
        assert parse_disk_and_partition("/dev/nvme0n1p2") == ("/dev/nvme0n1", "2")

    def test_invalid_path(self):
        assert parse_disk_and_partition("/dev/loop0") == (None, None)

    def test_empty_string(self):
        assert parse_disk_and_partition("") == (None, None)

    def test_no_partition_number(self):
        assert parse_disk_and_partition("/dev/mmcblk0") == (None, None)


class TestGetRootDevice:
    def test_success(self):
        result = subprocess.CompletedProcess(args=[], returncode=0, stdout="/dev/mmcblk0p2\n")
        with patch("rcp.utils.platform.subprocess.run", return_value=result) as mock_run:
            assert get_root_device() == "/dev/mmcblk0p2"
            mock_run.assert_called_once_with(
                ["findmnt", "-n", "-o", "SOURCE", "/"],
                capture_output=True, text=True, timeout=5,
            )

    def test_failure(self):
        result = subprocess.CompletedProcess(args=[], returncode=1, stdout="")
        with patch("rcp.utils.platform.subprocess.run", return_value=result):
            assert get_root_device() is None

    def test_timeout(self):
        with patch("rcp.utils.platform.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5)):
            assert get_root_device() is None

    def test_command_not_found(self):
        with patch("rcp.utils.platform.subprocess.run", side_effect=FileNotFoundError):
            assert get_root_device() is None


class TestGetBlockSizeBytes:
    def test_success(self):
        result = subprocess.CompletedProcess(args=[], returncode=0, stdout="31914983424\n")
        with patch("rcp.utils.platform.subprocess.run", return_value=result):
            assert get_block_size_bytes("/dev/mmcblk0") == 31914983424

    def test_failure(self):
        result = subprocess.CompletedProcess(args=[], returncode=1, stdout="")
        with patch("rcp.utils.platform.subprocess.run", return_value=result):
            assert get_block_size_bytes("/dev/mmcblk0") is None


class TestGetFilesystemUsage:
    def test_success(self):
        stdout = "     1B-blocks         Used        Avail\n 15720333312   3456789504  11448750080\n"
        result = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout)
        with patch("rcp.utils.platform.subprocess.run", return_value=result):
            usage = get_filesystem_usage("/dev/mmcblk0p2")
            assert usage == {
                "total": 15720333312,
                "used": 3456789504,
                "available": 11448750080,
            }

    def test_failure(self):
        result = subprocess.CompletedProcess(args=[], returncode=1, stdout="")
        with patch("rcp.utils.platform.subprocess.run", return_value=result):
            assert get_filesystem_usage("/dev/mmcblk0p2") is None


class TestFormatBytes:
    def test_gib(self):
        assert format_bytes(2 * 1024 ** 3) == "2.00 GiB"

    def test_gib_fractional(self):
        assert format_bytes(int(1.5 * 1024 ** 3)) == "1.50 GiB"

    def test_mib(self):
        assert format_bytes(512 * 1024 ** 2) == "512.00 MiB"

    def test_bytes(self):
        assert format_bytes(1023) == "1023 bytes"

    def test_none(self):
        assert format_bytes(None) == "N/A"

    def test_zero(self):
        assert format_bytes(0) == "0 bytes"
