from kivy.logger import Logger
from kivy.properties import StringProperty, ColorProperty
from rcp.components.popups.help_popup import HelpPopup  # noqa: F401
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ColorItem(BoxLayout):
    name = StringProperty()
    color = ColorProperty()
    help_file = StringProperty()

    def set_color(self, color: list[float]):
        log.debug(f"Color selected is {color}")
        self.color = color
