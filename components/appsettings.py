import os.path

from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings
import logging


log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

config = ConfigParser()
config.read(os.path.dirname(__file__) + "/../config.ini")


class AppSettings(Popup):
    settings = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Settings()
        self.settings.add_json_panel("Units", config, "data/units.json")
        self.settings.add_json_panel("Inputs", config, "data/inputs.json")
        self.settings.add_kivy_panel()
        self.settings.bind(on_close=self.close)
        self.add_widget(self.settings)

    def close(self, *args, **kv):
        self.dismiss()
