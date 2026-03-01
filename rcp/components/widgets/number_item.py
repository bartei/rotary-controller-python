from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


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
