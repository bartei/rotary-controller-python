from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty
from rcp.components.popups.help_popup import HelpPopup  # noqa: F401
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class StringItem(BoxLayout):
    name = StringProperty("")
    value = StringProperty("")
    disabled = BooleanProperty(False)
    help_file = StringProperty("")

    def set_value_from_text(self, text: str):
        try:
            self.value = text.encode("raw_unicode_escape").decode("unicode_escape")
        except (UnicodeDecodeError, UnicodeEncodeError):
            self.value = text
