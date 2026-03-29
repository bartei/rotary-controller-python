from kivy.logger import Logger
from kivy.properties import BooleanProperty, StringProperty, ColorProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from rcp.components.widgets.beep_mixin import BeepMixin
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class LedButton(BeepMixin, ButtonBehavior, BoxLayout):
    label = StringProperty()
    checkbox_value = BooleanProperty()
    current_color = ColorProperty((0, 0, 0, 1))

    def on_checkbox_value(self, instance, value):
        if value:
            self.current_color = self.color_on
        else:
            self.current_color = self.color_off
