import os
from distutils.dep_util import newer

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class SetupPopup(Popup):
    screen_manager: ScreenManager = ObjectProperty()
    screen_selector: BoxLayout = ObjectProperty()

    def on_dismiss(self):
        log.debug("Close setup page")
        network_panels = [item for item in self.ids['screen_manager'].screens if item.name == "network"]

        # Network panel screen is instantiated, get a reference to its NetworkPanel Instance
        if len(network_panels) == 1:
            network_panel = network_panels[0].children[0]
            network_panel.on_dismiss(self, None)