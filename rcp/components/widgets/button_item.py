import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


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