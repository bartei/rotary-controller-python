import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class NumberItem(BoxLayout):
    name = StringProperty("")
    value = NumericProperty(0.0)
    integer = BooleanProperty(False)
    help_file = StringProperty("")

    def validate(self, value):
        try:
            if isinstance(value, str) and "." in value:
                self.value = float(value)
            elif isinstance(value, float):
                self.value = float(value)
            else:
                self.value = int(value)
        except Exception as e:
            log.error(e.__str__())

    def on_value(self, instance, value):
        self.validate(value)
