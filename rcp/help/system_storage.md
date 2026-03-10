System Storage
==============

View storage information and resize the root partition on a
Raspberry Pi. This screen is only available on Raspberry Pi
hardware.

## Storage Devices

Read-only information about the Pi's storage:
- **Root Device** — the partition mounted as /
- **Disk Device** — the physical storage device (e.g., /dev/mmcblk0)
- **Partition Number** — which partition on the disk
- **Disk Size** — total capacity of the storage device
- **Partition Size** — current size of the root partition

## Filesystem Usage

Current disk space usage of the root filesystem:
- **Total** — total available space on the partition
- **Used** — space currently in use
- **Free** — remaining free space

## Resize Root Partition

If the root partition does not use the full disk (common after
flashing a new SD card image), you can expand it to use all
available space.

### Refresh Storage Info
Re-reads the current storage state.

### Resize Partition
Expands the root partition to fill the entire disk. This runs
`growpart` and `resize2fs` and shows status below.

- Button shows "Resize" when expansion is possible
- Button shows "Already full" when the partition already uses
  the full disk
- Button shows "Running..." during the resize operation

## Notes

- Resizing is safe — it only expands, never shrinks
- The operation takes a few seconds and does not require a reboot
- Only available on Raspberry Pi (hidden on other platforms)