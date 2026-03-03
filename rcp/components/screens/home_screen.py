from keke import TraceOutput
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from rcp.components.home.coordbar import CoordBar
from rcp.components.home.servobar import ServoBar
from rcp.components.home.jogbar import JogBar
from rcp.components.home.statusbar import StatusBar
from rcp.components.home.elsbar import ElsBar
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class HomePage(Screen):
    device = ObjectProperty()
    servo = ObjectProperty()

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)

        self.bars_container = self.ids['bars_container']
        self.status_bar = StatusBar()
        self.bars_container.add_widget(self.status_bar)
        self.els_bar = ElsBar(id_override="0")
        self.jog_bar = JogBar()

        # Configure Current Mode, and disable Indexing mode if servo is set to ELS
        self.next_mode = self.app.current_mode
        if self.app.servo.elsMode and self.next_mode == 1:
            self.next_mode = 2

        self.coord_bars = []
        self.servo_bar = ServoBar()
        # The "mode bar" is the bottom widget that swaps between servo/els/jog
        self.mode_bar = self.servo_bar

        self._build_coord_bars()
        self.bars_container.add_widget(self.servo_bar)

        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.app.bind(current_mode=self.change_mode)
        self.app.bind(axes=self._on_axes_changed)
        self.change_mode(self, self.next_mode)

    def _build_coord_bars(self):
        """Create CoordBar widgets for each axis and add them to the container."""
        for axis_disp in self.app.axes:
            cb = CoordBar(axis=axis_disp)
            self.coord_bars.append(cb)
            self.bars_container.add_widget(cb)

    def _on_axes_changed(self, instance, value):
        """Rebuild coord bars when the axes list changes."""
        # Remove old coord bars
        for cb in self.coord_bars:
            self.bars_container.remove_widget(cb)
        self.coord_bars.clear()

        # Remove the mode bar (bottom widget) so we can re-add it after new coord bars
        self.bars_container.remove_widget(self.mode_bar)

        # Rebuild
        self._build_coord_bars()

        # Re-add the current mode bar at the bottom
        self.bars_container.add_widget(self.mode_bar)

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
        self.app.servo.servoEnable = 0

        # Swap the bottom mode bar
        self.bars_container.remove_widget(self.mode_bar)
        if self.next_mode == 1:  # IDX
            self.mode_bar = self.servo_bar
        elif self.next_mode == 2:  # ELS
            self.mode_bar = self.els_bar
        elif self.next_mode == 3:  # JOG
            self.mode_bar = self.jog_bar
        self.bars_container.add_widget(self.mode_bar)

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
