import os

from keke import TraceOutput
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from rcp.components.home.jogbar import JogBar
from rcp.components.home.statusbar import StatusBar
from rcp.components.home.elsbar import ElsBar

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class HomePage(Screen):
    device = ObjectProperty()
    servo = ObjectProperty()

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)

        self.bars_container = self.ids['bars_container']
        self.bars_container.add_widget(StatusBar())
        self.els_bar = ElsBar(id_override="0")
        self.jog_bar = JogBar()

        # Configure Current Mode, and disable Indexing mode if servo is set to ELS
        self.next_mode = self.app.current_mode
        if self.app.servo.elsMode and self.next_mode == 1:
            self.next_mode = 2

        coord_bars = []
        for scale in self.app.scales:
            self.bars_container.add_widget(scale)

        self.scales = coord_bars
        self.bars_container.add_widget(self.app.servo)

        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.app.bind(current_mode=self.change_mode)
        self.change_mode(self, self.next_mode)

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

        # Visualize things properly
        if self.next_mode == 1: # IDX
            self.bars_container: BoxLayout
            self.bars_container.remove_widget(self.bars_container.children[0])
            self.bars_container.add_widget(self.app.servo)
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
