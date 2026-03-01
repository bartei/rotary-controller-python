from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ButtonItem(BoxLayout):
    name = StringProperty("")
    value = StringProperty("")
    help_file = StringProperty("")

    def __init__(self, **kv):
        super().__init__(**kv)
        self.register_event_type("on_release")

    def on_release(self):
        """Default event handler. Can be overridden in KV or Python."""
        pass

    def dispatch_release(self):
        self.dispatch("on_release")  # Trigger the event