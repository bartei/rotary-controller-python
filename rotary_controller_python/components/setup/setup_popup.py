import os

from kivy.app import App
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
        current_app = App.get_running_app()
        current_app.manual_full_update()
        log.info("Close setup page")
