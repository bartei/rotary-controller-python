import asyncio
import importlib.metadata
import os
import subprocess

import aiohttp
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

DEV_RELEASE = "dev (experimental)"


class UpdateScreen(Screen):
    releases = ListProperty([])
    selected_release = StringProperty("")
    current_release = StringProperty("v" + importlib.metadata.version("rcp"))
    enable_update_button = BooleanProperty(False)
    allow_experimental = BooleanProperty(False)
    status = StringProperty("")

    def __init__(self, **kv):
        super().__init__(**kv)
        self.schedule_refresh_releases()
        self.status = ""

    def schedule_refresh_releases(self):
        log.info("User wants to install a different release!")
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.refresh_releases(dt)))

    async def refresh_releases(self, dt):
        self.update_status("Retrieve all the releases from Github")
        url = "https://api.github.com/repos/bartei/rotary-controller-python/releases"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        text = await response.text()
                        log.error(f"Failed to fetch releases: {response.status} - {text}")
                        return

                    releases = (await response.json())[:10]

            # Get only official releases
            official = [item['tag_name'] for item in releases if item['prerelease'] == False]
            self._set_releases(official)
            self.selected_release = official[0] if official else ""
        except Exception as e:
            self.update_status(str(e))

    def _set_releases(self, official: list[str]):
        """Set the releases list, appending the dev entry if experimental is enabled."""
        if self.allow_experimental:
            self.releases = official + [DEV_RELEASE]
        else:
            self.releases = official

    def on_selected_release(self, instance, value):
        log.info(f"Selected release: {self.selected_release}")
        if value != "" and value != self.current_release:
            self.enable_update_button = True
        else:
            self.enable_update_button = False

    def update_status(self, status: str):
        self.status = self.status + status + "\n"

    def on_allow_experimental(self, instance, value):
        # Rebuild the list from the current official releases
        official = [r for r in self.releases if r != DEV_RELEASE]
        self._set_releases(official)
        if not value and self.selected_release == DEV_RELEASE:
            self.selected_release = self.releases[0] if self.releases else ""

    def install_release(self):
        log.info("User wants to install a different release!")
        if self.selected_release == DEV_RELEASE:
            self._confirm_dev_install()
        else:
            self._do_install()

    def _confirm_dev_install(self):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        content.add_widget(Label(
            text=(
                "Warning: You are about to install an experimental version.\n\n"
                "- Development version may be unstable or incomplete\n"
                "- Features may not work as expected\n"
                "- Data or settings could be corrupted\n"
                "- You may need to reinstall a stable version to recover"
            ),
            halign="left",
            valign="top",
            text_size=(None, None),
        ))

        buttons = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=60)
        btn_cancel = Button(text="Cancel", font_size=22)
        btn_confirm = Button(text="Install Anyway", font_size=22)
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_confirm)
        content.add_widget(buttons)

        popup = Popup(
            title="Warning: Experimental Version",
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=False,
        )

        btn_cancel.bind(on_release=popup.dismiss)
        btn_confirm.bind(on_release=lambda _: (popup.dismiss(), self._do_install()))

        popup.open()

    def _do_install(self):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_install(dt)))

    async def perform_install(self, dt):
        self.update_status(f"Performing installation of a new release: {self.current_release} -> {self.selected_release}")

        project_folder = "/rotary-controller-python"
        if not os.path.isdir(project_folder):
            self.update_status(f"Project folder not found at the expected location: {project_folder}")
            return

        self.update_status(f"Found project folder at: {project_folder}")
        os.chdir(project_folder)

        if self.selected_release == DEV_RELEASE:
            commands = [
                "git remote set-branches origin '*'",
                "git fetch --all",
                "git checkout dev",
                "git pull origin dev",
                "pip install .",
                "reboot",
            ]
        else:
            commands = [
                "git fetch --all --tags",
                f"git checkout tags/{self.selected_release}",
                "pip install .",
                "reboot",
            ]

        for c in commands:
            self.update_status(f"run: {c}")
            p = subprocess.Popen(
                c,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            while p.poll() is None:
                await asyncio.sleep(1)

            output = p.stdout.read().decode()
            log.info(output)
            self.update_status(f"return code: {p.returncode}")
            self.update_status(f"output: {output}")

            if p.stderr is not None:
                error = p.stderr.read().decode()
                log.error(output)
                self.update_status(f"err: {error}")

            if p.returncode != 0:
                return
