import logging
import os

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, ColorProperty


log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class LabelCheckBox(BoxLayout):
    label = StringProperty()
    checkbox_value = BooleanProperty()
    current_color = ColorProperty((0, 0, 0, 1))

    def on_checkbox_value(self, instance, value):
        if value:
            self.current_color = (1, 1, 1, 1)
        else:
            self.current_color = (0, 0, 0, 1)
