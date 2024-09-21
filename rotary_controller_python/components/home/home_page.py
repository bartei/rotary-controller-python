import os
from contextlib import ExitStack

from keke import TraceOutput
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import (
    ListProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout

from rotary_controller_python.components.coordbar import CoordBar
from rotary_controller_python.components.servobar import ServoBar
from rotary_controller_python.components.statusbar import StatusBar

log = Logger.getChild(__name__)

current_app = App.get_running_app()
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class HomePage(BoxLayout):
    device = ObjectProperty()
    bars_container = ObjectProperty()
    servo = ObjectProperty()
    scales = ListProperty([])

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        self.bars_container.add_widget(StatusBar())
        servo_bar = ServoBar(servo=self.servo)

        coord_bars = []
        for i in range(4):
            bar = CoordBar(inputIndex=i, device=self.device, id_override=f"{i}", servo=self.servo)
            coord_bars.append(bar)
            self.bars_container.add_widget(bar)

        self.scales = coord_bars
        self.bars_container.add_widget(servo_bar)

        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.exit_stack = ExitStack()

    def on_touch_down(self, touch):
        self.app.beep()
        return super().on_touch_down(touch)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if text == "t" and "ctrl" in modifiers:
            self.exit_stack.enter_context(TraceOutput(file=open("trace.out", "w")))
            return True  # Return True to accept the key. False would reject the key press.
