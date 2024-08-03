import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class DualNumberItem(BoxLayout):
    name = StringProperty("")
    value = NumericProperty(0.0)
    ratio = NumericProperty(1.0)
    scaled_value = NumericProperty(0.0)

    def on_value(self, instance, value):
        try:
            self.scaled_value = value / self.ratio
        except Exception as e:
            log.error(e.__str__())

    def on_scaled_value(self, instance, value):
        try:
            self.value = value * self.ratio
        except Exception as e:
            log.error(e.__str__())