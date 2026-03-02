import re
import subprocess

from kivy.logger import Logger

log = Logger.getChild(__name__)


def is_raspberry_pi() -> bool:
    """Check if running on a Raspberry Pi by reading the device-tree model."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            model = f.read().strip("\x00").strip()
        return model.startswith("Raspberry Pi")
    except (FileNotFoundError, PermissionError):
        return False


def get_root_device() -> str | None:
    """Get the device backing the root filesystem, e.g. '/dev/mmcblk0p2'."""
    try:
        result = subprocess.run(
            ["findmnt", "-n", "-o", "SOURCE", "/"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log.error(f"Failed to get root device: {e}")
    return None


def parse_disk_and_partition(device: str) -> tuple[str, str] | tuple[None, None]:
    """Parse a block device path into (disk, partition_number).

    Supports mmcblk-style (/dev/mmcblk0p2) and sd-style (/dev/sda2) paths.
    """
    # mmcblk style: /dev/mmcblk0p2 -> (/dev/mmcblk0, 2)
    m = re.match(r"^(/dev/mmcblk\d+)p(\d+)$", device)
    if m:
        return m.group(1), m.group(2)

    # sd style: /dev/sda2 -> (/dev/sda, 2)
    m = re.match(r"^(/dev/sd[a-z]+)(\d+)$", device)
    if m:
        return m.group(1), m.group(2)

    # nvme style: /dev/nvme0n1p2 -> (/dev/nvme0n1, 2)
    m = re.match(r"^(/dev/nvme\d+n\d+)p(\d+)$", device)
    if m:
        return m.group(1), m.group(2)

    return None, None


def get_block_size_bytes(device: str) -> int | None:
    """Get the total size in bytes of a block device using lsblk."""
    try:
        result = subprocess.run(
            ["lsblk", "-b", "-n", "-o", "SIZE", device],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            line = result.stdout.strip().splitlines()[0]
            return int(line.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError) as e:
        log.error(f"Failed to get block size for {device}: {e}")
    return None


def get_filesystem_usage(device: str) -> dict | None:
    """Get filesystem usage stats for a device.

    Returns dict with 'total', 'used', 'available' in bytes, or None on failure.
    """
    try:
        result = subprocess.run(
            ["df", "-B1", "--output=size,used,avail", device],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            if len(lines) >= 2:
                parts = lines[1].split()
                return {
                    "total": int(parts[0]),
                    "used": int(parts[1]),
                    "available": int(parts[2]),
                }
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError) as e:
        log.error(f"Failed to get filesystem usage for {device}: {e}")
    return None


def format_bytes(n: int | None) -> str:
    """Format a byte count as a human-readable string (GiB or MiB)."""
    if n is None:
        return "N/A"
    if n >= 1024 ** 3:
        return f"{n / 1024 ** 3:.2f} GiB"
    if n >= 1024 ** 2:
        return f"{n / 1024 ** 2:.2f} MiB"
    return f"{n} bytes"
