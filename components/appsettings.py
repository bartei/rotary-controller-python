import os.path

from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings
import logging

INPUTS_COUNT = 4

log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

config = ConfigParser()
config.read(os.path.dirname(__file__) + "/../config.ini")


def generate_input_defaults(my_config: ConfigParser):
    for item in range(INPUTS_COUNT):
        my_config.setdefaults(
            section=f"input{item+1}",
            keyvalues={
                "axis_name": "X",
                "ratio_num": 1,
                "ratio_den": 100,
                "sync_num": 1,
                "sync_den": 100,
                "sync_enable": "normal",
            }
        )


generate_input_defaults(config)


def generate_input_json() -> str:
    import json

    result_dict = []
    for item in range(INPUTS_COUNT):
        section = f"input{item+1}"
        result_dict.append({
            "type": "title",
            "title": f"Input {item+1}"
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
        result_dict.append(
            {
                "type": "numeric",
                "title": "Scale Ratio Denominator",
                "desc": "The scale/encoder denominator when converting counts to units",
                "section": section,
                "key": "ratio_den"
            }
        )
        result_dict.append(
            {
                "type": "numeric",
                "title": "Synchro mode ratio Numerator",
                "desc": "The ratio numerator when using this input as a synchro reference",
                "section": section,
                "key": "sync_num"
            }
        )
        result_dict.append(
            {
                "type": "numeric",
                "title": "Synchro mode ratio Denominator",
                "desc": "The ratio denominator when using this input as a synchro reference",
                "section": section,
                "key": "sync_den"
            }
        )
        result_dict.append(
            {
                "type": "string",
                "title": "Enable Sync Mode",
                "desc": "Enable flag to use this input for the sync mode",
                "section": section,
                "key": "sync_enable"
            }
        )

    result_json = json.dumps(result_dict)
    return result_json


class AppSettings(Popup):
    settings = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Settings()
        self.settings.add_json_panel("Units", config, "data/units.json")
        self.settings.add_json_panel("Inputs", config, data=generate_input_json())
        self.settings.add_json_panel("Rotary", config, "data/rotary.json")
        self.settings.add_kivy_panel()
        self.settings.bind(on_close=self.close)
        self.add_widget(self.settings)

    def close(self, *args, **kv):
        self.dismiss()
