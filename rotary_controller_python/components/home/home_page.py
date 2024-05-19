import os
from contextlib import ExitStack

from keke import TraceOutput
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import (
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)

current_app = App.get_running_app()
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class HomePage(BoxLayout):
    device = ObjectProperty()
    status_bar = ObjectProperty()
    scale_x = ObjectProperty()
    scale_y = ObjectProperty()
    scale_z = ObjectProperty()
    scale_a = ObjectProperty()
    servo = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.exit_stack = ExitStack()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if text == "t" and "ctrl" in modifiers:
            self.exit_stack.enter_context(TraceOutput(file=open("trace.out", "w")))
            return True  # Return True to accept the key. False would reject the key press.
