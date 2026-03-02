import asyncio
import subprocess

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv
from rcp.utils.platform import (
    is_raspberry_pi,
    get_root_device,
    parse_disk_and_partition,
    get_block_size_bytes,
    get_filesystem_usage,
    format_bytes,
)

log = Logger.getChild(__name__)
load_kv(__file__)

# Threshold: if partition uses >= 99% of disk, no resize needed
RESIZE_THRESHOLD = 0.99


class SystemScreen(Screen):
    is_pi = BooleanProperty(False)
    root_device = StringProperty("N/A")
    disk_device = StringProperty("N/A")
    partition_number = StringProperty("N/A")
    disk_size_str = StringProperty("N/A")
    partition_size_str = StringProperty("N/A")
    fs_total_str = StringProperty("N/A")
    fs_used_str = StringProperty("N/A")
    fs_free_str = StringProperty("N/A")
    status = StringProperty("")
    can_resize = BooleanProperty(False)
    is_running = BooleanProperty(False)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.is_pi = is_raspberry_pi()
        if self.is_pi:
            Clock.schedule_once(lambda dt: self.refresh_storage_info())

    def refresh_storage_info(self):
        root_dev = get_root_device()
        if not root_dev:
            self.log("Could not determine root device")
            return

        self.root_device = root_dev
        disk, part_num = parse_disk_and_partition(root_dev)

        if disk and part_num:
            self.disk_device = disk
            self.partition_number = part_num
        else:
            self.log(f"Could not parse disk/partition from {root_dev}")
            return

        disk_size = get_block_size_bytes(disk)
        part_size = get_block_size_bytes(root_dev)

        self.disk_size_str = format_bytes(disk_size)
        self.partition_size_str = format_bytes(part_size)

        usage = get_filesystem_usage(root_dev)
        if usage:
            self.fs_total_str = format_bytes(usage["total"])
            self.fs_used_str = format_bytes(usage["used"])
            self.fs_free_str = format_bytes(usage["available"])

        # Determine if resize is possible
        if disk_size and part_size:
            ratio = part_size / disk_size
            self.can_resize = ratio < RESIZE_THRESHOLD
        else:
            self.can_resize = False

    def log(self, message: str):
        log.info(message)
        self.status += f"{message}\n"

    def prompt_resize(self):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        btn_cancel = Button(text="Cancel", font_size=22)
        btn_confirm = Button(text="Confirm Resize", font_size=22)

        content.add_widget(btn_confirm)
        content.add_widget(btn_cancel)

        popup = Popup(
            title="Resize root partition to fill the entire disk?",
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False,
        )

        btn_cancel.bind(on_release=popup.dismiss)
        btn_confirm.bind(on_release=lambda _: self._start_resize(popup))

        popup.open()

    def _start_resize(self, popup):
        popup.dismiss()
        self.is_running = True
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._perform_resize()))

    async def _perform_resize(self):
        self.status = ""
        self.log("Starting partition resize...")

        # Step 1: growpart
        self.log(f"Running: growpart {self.disk_device} {self.partition_number}")
        try:
            p = subprocess.Popen(
                ["growpart", self.disk_device, self.partition_number],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            while p.poll() is None:
                await asyncio.sleep(1)

            stdout = p.stdout.read().decode() if p.stdout else ""
            stderr = p.stderr.read().decode() if p.stderr else ""

            if stdout:
                self.log(stdout.strip())
            if stderr:
                self.log(stderr.strip())

            if p.returncode != 0:
                self.log(f"growpart failed with return code {p.returncode}")
                self.is_running = False
                return
            self.log("growpart completed successfully")
        except FileNotFoundError:
            self.log("growpart not found - install cloud-guest-utils")
            self.is_running = False
            return

        # Step 2: resize2fs
        self.log(f"Running: resize2fs {self.root_device}")
        try:
            p = subprocess.Popen(
                ["resize2fs", self.root_device],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            while p.poll() is None:
                await asyncio.sleep(1)

            stdout = p.stdout.read().decode() if p.stdout else ""
            stderr = p.stderr.read().decode() if p.stderr else ""

            if stdout:
                self.log(stdout.strip())
            if stderr:
                self.log(stderr.strip())

            if p.returncode != 0:
                self.log(f"resize2fs failed with return code {p.returncode}")
                self.is_running = False
                return
            self.log("resize2fs completed successfully")
        except FileNotFoundError:
            self.log("resize2fs not found - install e2fsprogs")
            self.is_running = False
            return

        self.log("Resize complete! Refreshing storage info...")
        self.refresh_storage_info()
        self.is_running = False
