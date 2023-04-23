import os.path

from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingsWithSidebar
from loguru import logger as log

INPUTS_COUNT = 4

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

config_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "config.ini"
    )
)
config = ConfigParser()
config.read(config_path)

sections = [f"input{item}" for item in range(INPUTS_COUNT)]

# Check if the sections exist and add them if they don't
for section in sections:
    if not config.has_section(section):
        config.add_section(section)

config.write()


def generate_input_json() -> str:
    import json

    result_dict = []
    for item in range(INPUTS_COUNT):
        section = f"input{item}"
        result_dict.append({
            "type": "title",
            "title": f"Input {item}"
        })
        result_dict.append({
            "type": "string",
            "title": "Axis Name",
            "desc": "The name of this axis, ex: X",
            "section": section,
            "key": "axis_name"
        })
        result_dict.append({
            "type": "numeric",
            "title": "Scale Ratio Numerator",
            "desc": "The scale/encoder numerator when converting counts to units",
            "section": section,
            "key": "ratio_num"
        })
        result_dict.append({
                "type": "numeric",
                "title": "Scale Ratio Denominator",
                "desc": "The scale/encoder denominator when converting counts to units",
                "section": section,
                "key": "ratio_den"
        })

    result_json = json.dumps(result_dict)
    return result_json


class AppSettings(SettingsWithSidebar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        data_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "data"
            )
        )
        self.add_json_panel("Units", config, os.path.join(data_path, "units.json"))
        self.add_json_panel("Inputs", config, data=generate_input_json())
        self.add_json_panel("Rotary", config, os.path.join(data_path, "rotary.json"))
        self.add_kivy_panel()
        self.bind(on_close=self.close)
        # self.add_widget(self.settings)

    def close(self, *args, **kv):
        self.parent.parent.parent.dismiss()
