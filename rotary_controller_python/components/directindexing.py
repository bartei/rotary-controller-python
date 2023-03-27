import logging
import os

from kivy.lang import Builder
from kivy.properties import StringProperty, ConfigParserProperty
from kivy.uix.boxlayout import BoxLayout
from rotary_controller_python.config import config


log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class DirectIndexing(BoxLayout):
    input_name = StringProperty()
    display_color = ConfigParserProperty(
        defaultvalue="#ffffffff",
        section="formatting",
        key="display_color",
        config=config
    )
