import os.path

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings
import logging

INPUTS_COUNT = 4

log = logging.getLogger(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


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
        result_dict.append({
                "type": "numeric",
                "title": "Scale Ratio Denominator",
                "desc": "The scale/encoder denominator when converting counts to units",
                "section": section,
                "key": "ratio_den"
        })

    result_json = json.dumps(result_dict)
    return result_json


class AppSettings(Popup):
    settings = None

    def __init__(self, **kwargs):
        from rotary_controller_python.config import config
        super().__init__(**kwargs)
        self.settings = Settings()
        self.settings.add_json_panel("Units", config, "rotary_controller_python/data/units.json")
        self.settings.add_json_panel("Inputs", config, data=generate_input_json())
        self.settings.add_json_panel("Rotary", config, "rotary_controller_python/data/rotary.json")
        self.settings.add_kivy_panel()
        self.settings.bind(on_close=self.close)
        self.add_widget(self.settings)

    def close(self, *args, **kv):
        self.dismiss()
