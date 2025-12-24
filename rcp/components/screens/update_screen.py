import asyncio
import os
import importlib.metadata
import subprocess

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
import requests

from kivy.clock import Clock

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class UpdateScreen(Screen):
    releases = ListProperty([])
    selected_release = StringProperty("")
    current_release = StringProperty("v" + importlib.metadata.version("rcp"))
    enable_update_button = BooleanProperty(False)
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
        url = f"https://api.github.com/repos/bartei/rotary-controller-python/releases"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                log.error(f"Failed to fetch releases: {response.status_code} - {response.text}")
                return

            releases = response.json()[:10]

            # Get only official releases
            releases = [item['tag_name'] for item in releases if item['prerelease'] == False]
            # releases = [item['tag_name'] for item in releases]
            self.releases = releases
            self.selected_release = releases[0]
        except Exception as e:
            self.update_status(e.__str__())

    def on_selected_release(self, instance, value):
        log.info(f"Selected release: {self.selected_release}")
        if value != "" and value != self.current_release:
            self.enable_update_button = True
        else:
            self.enable_update_button = False

    def update_status(self, status: str):
        self.status = self.status + status + "\n"

    def install_release(self):
        log.info("User wants to install a different release!")
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_install(dt)))

    async def perform_install(self, dt):
        self.update_status(f"Performing installation of a new release: {self.current_release} -> {self.selected_release}")

        project_folder = "/rotary-controller-python"
        if not os.path.isdir(project_folder):
            self.update_status(f"Project folder not found at the expected location: {project_folder}")
            return

        self.update_status(f"Found project folder at: {project_folder}")
        os.chdir(project_folder)

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
