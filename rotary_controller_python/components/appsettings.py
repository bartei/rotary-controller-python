import os.path

from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.uix.settings import SettingsWithSidebar
from loguru import logger as log

INPUTS_COUNT = 4

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")
)
config = ConfigParser()
config.read(config_path)


class AppSettings(SettingsWithSidebar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data")
        )
        self.add_json_panel("Units", config, os.path.join(data_path, "units.json"))
        self.add_kivy_panel()
        self.bind(on_close=self.close)

    def close(self, *args, **kv):
        self.parent.parent.parent.dismiss()
