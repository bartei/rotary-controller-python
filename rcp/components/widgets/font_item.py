from kivy.logger import Logger
from kivy.properties import StringProperty
from rcp.components.popups.help_popup import HelpPopup  # noqa: F401
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class FontItem(BoxLayout):
    name = StringProperty("")
    font_path = StringProperty("fonts/iosevka-regular.ttf")
    help_file = StringProperty("")

    def set_font(self, font_path: str):
        log.debug(f"Font selected: {font_path}")
        self.font_path = font_path
