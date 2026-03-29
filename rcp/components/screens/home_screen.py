from keke import TraceOutput
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from rcp.components.home.dro_mode_layout import DroModeLayout
from rcp.components.home.els_mode_layout import ElsModeLayout
from rcp.components.home.elsbar import ElsBar
from rcp.components.home.index_mode_layout import IndexModeLayout
from rcp.components.home.jog_mode_layout import JogModeLayout
from rcp.components.home.statusbar import StatusBar
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

        # Create shared ElsBar (has SavingDispatcher state)
        self.els_bar = ElsBar(id_override="0")

        # Create all mode layouts once
        self.mode_layouts = {
            1: IndexModeLayout(),
            2: ElsModeLayout(els_bar=self.els_bar),
            3: JogModeLayout(),
            4: DroModeLayout(),
        }

        # Configure initial mode, disable Indexing if servo is in ELS mode
        self.next_mode = self.app.current_mode
        if self.app.servo.elsMode and self.next_mode == 1:
            self.next_mode = 2

        self.current_layout = None
        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.app.bind(current_mode=self.change_mode)
        self.app.bind(axes=self._on_axes_changed)
        self.change_mode(self, self.next_mode)

    def _on_axes_changed(self, instance, value):
        """Rebuild axis bars in all mode layouts when the axes list changes."""
        for layout in self.mode_layouts.values():
            layout.rebuild_axes()

    def change_mode(self, instance, value):
        self.next_mode = value
        if self.app.servo.servoEnable != 0:
            self.app.servo.jogSpeed = 0
        Clock.schedule_once(self.change_mode_speed_check, 0.1)

    def change_mode_speed_check(self, instance):
        if self.app.servo.speed != 0:
            Clock.schedule_once(self.change_mode_speed_check, 0.1)
            return

        # Reset enables
        jog_layout = self.mode_layouts[3]
        jog_layout.jog_bar.enable_jog = False
        self.app.servo.servoEnable = 0

        # Swap the entire mode layout
        if self.current_layout is not None:
            self.bars_container.remove_widget(self.current_layout)

        self.current_layout = self.mode_layouts.get(self.next_mode)
        if self.current_layout is not None:
            self.bars_container.add_widget(self.current_layout)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if text == "t" and "ctrl" in modifiers:
            self.exit_stack.enter_context(TraceOutput(file=open("trace.out", "w")))
            return True
