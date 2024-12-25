import asyncio
import time
from contextlib import ExitStack

from keke import TraceOutput
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import (
    ObjectProperty,
)
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout

from rcp.components.home.coordbar import CoordBar
from rcp.components.home.jogbar import JogBar
from rcp.components.home.servobar import ServoBar
from rcp.components.home.statusbar import StatusBar
from rcp.components.home.elsbar import ElsBar
from rcp.components.home.home_toolbar import HomeToolbar

log = Logger.getChild(__name__)


class HomePage(BoxLayout):
    device = ObjectProperty()
    servo = ObjectProperty()
    orientation = "horizontal"

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        self.bars_container = BoxLayout(
            orientation="vertical",
            size_hint_y=1,
            size_hint_x=1,
        )
        toolbar = HomeToolbar()
        self.add_widget(toolbar)
        self.add_widget(self.bars_container)
        self.bars_container.add_widget(StatusBar())
        self.servo_bar = ServoBar(servo=self.servo)
        self.els_bar = ElsBar()
        self.jog_bar = JogBar()

        coord_bars = []
        for i in range(4):
            bar = bar = CoordBar(inputIndex=i, device=self.device, id_override=f"{i}", servo=self.servo)
            coord_bars.append(bar)
            self.bars_container.add_widget(bar)

        self.scales = coord_bars
        self.bars_container.add_widget(self.servo_bar)

        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.exit_stack = ExitStack()
        self.app.bind(current_mode=self.change_mode)

    def change_mode(self, instance, value):
        self.next_mode = value
        if self.app.servo.servoEnable != 0:
            self.app.servo.jogSpeed = 0

        Clock.schedule_once(self.change_mode_speed_check, 0.1)


    def change_mode_speed_check(self, instance):
        if self.app.servo.speed != 0:
            Clock.schedule_once(self.change_mode_speed_check, 0.1)
            return

        # Reset all the enables
        self.jog_bar.enable_jog = False
        self.servo_bar.servo.servoEnable = 0

        # Visualize things properly
        if self.next_mode == 1: # IDX
            self.bars_container: BoxLayout
            self.bars_container.remove_widget(self.bars_container.children[0])
            self.bars_container.add_widget(self.servo_bar)
        if self.next_mode == 2: # ELS
            self.bars_container: BoxLayout
            self.bars_container.remove_widget(self.bars_container.children[0])
            self.bars_container.add_widget(self.els_bar)
        if self.next_mode == 3: # JOG
            self.bars_container: BoxLayout
            self.bars_container.remove_widget(self.bars_container.children[0])
            self.bars_container.add_widget(self.jog_bar)


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
