import asyncio
import os
import importlib.metadata
import subprocess
import time
from sys import stdout

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty, ListProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
import threading
import requests

from kivy.clock import Clock, mainthread

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class FormatsPanel(BoxLayout):
    formats = ObjectProperty()
    releases = ListProperty([])
    selected_release = StringProperty("")
    current_release = StringProperty("v" + importlib.metadata.version("rcp"))
    enable_update_button = BooleanProperty(False)
    status = StringProperty("")

    def __init__(self, formats, **kv):
        self.formats = formats
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))
        threading.Thread(target=self.fetch_releases).start()
        self.status = ""

    def fetch_releases(self):
        self.update_status("Retrieve all the releases from Github")
        url = f"https://api.github.com/repos/bartei/rotary-controller-python/releases"
        response = requests.get(url)
        if response.status_code != 200:
            log.error(f"Failed to fetch releases: {response.status_code} - {response.text}")
            return

        releases = response.json()[:10]
        # Get only official releases
        # releases = [item['tag_name'] for item in releases if item['prerelease'] == False]
        releases = [item['tag_name'] for item in releases]

        # Get the current version of the rcp package:
        self.update_releases(releases)

    def on_selected_release(self, instance, value):
        log.info(f"Selected release: {self.selected_release}")
        if value != "" and value != self.current_release:
            self.enable_update_button = True
        else:
            self.enable_update_button = False

    @mainthread
    def update_releases(self, releases: list[str]):
        self.releases = releases

    @mainthread
    def update_status(self, status: str):
        self.status = self.status + status + "\n"

    def install_release(self):
        log.info("User wants to install a different release!")
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_install(dt)))

    async def perform_install(self, dt):
        self.update_status(f"Performing installation of a new release: {self.current_release} -> {self.selected_release}")

        project_folder = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            ".."
        ))

        os.chdir(project_folder)
        self.update_status(f"Found project folder at: {project_folder}")

        commands = [
            "git fetch --all --tags",
            f"git checkout tags/{self.selected_release}",
            "pip install .",
            "reboot"
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
