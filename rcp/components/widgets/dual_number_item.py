from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class DualNumberItem(BoxLayout):
    name = StringProperty("")
    value = NumericProperty(0.0)
    ratio = NumericProperty(1.0)
    scaled_value = NumericProperty(0.0)

    def on_value(self, instance, value):
        try:
            self.scaled_value = value / self.ratio
        except Exception as e:
            log.error(str(e))

    def on_scaled_value(self, instance, value):
        try:
            self.value = value * self.ratio
        except Exception as e:
            log.error(str(e))