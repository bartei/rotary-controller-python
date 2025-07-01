import asyncio
import time
from contextlib import ExitStack

from keke import TraceOutput
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from rcp.components.home.jogbar import JogBar
from rcp.components.home.statusbar import StatusBar
from rcp.components.home.elsbar import ElsBar
from rcp.components.home.home_toolbar import HomeToolbar
from rcp.components.home.placeholder_widget import PlaceholderWidget

log = Logger.getChild(__name__)


class HomePage(BoxLayout):
    device = ObjectProperty()
    servo = ObjectProperty()
    orientation = "horizontal"

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
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
        self.els_bar = ElsBar(id_override="0")
        self.jog_bar = JogBar()

        # Configure Current Mode, and disable Indexing mode if servo is set to ELS
        self.next_mode = self.app.current_mode
        if self.app.servo.elsMode and self.next_mode == 1:
            self.next_mode = 2

        coord_bars = []
        self.scale_placeholders = {}  # Dictionary to keep track of placeholders for scales
        for scale in self.app.scales:
            if scale.axisName.strip():  # Only add the scale if it has a non-empty axisName
                self.bars_container.add_widget(scale)
                coord_bars.append(scale)
                # Bind to the axisName property to update visibility when it changes
                scale.bind(axisName=self.on_scale_axis_name_changed)
            else:
                # Add a placeholder widget instead of the scale
                placeholder = PlaceholderWidget()
                self.bars_container.add_widget(placeholder)
                self.scale_placeholders[scale] = placeholder
                # Bind to the axisName property to update visibility when it changes
                scale.bind(axisName=self.on_scale_axis_name_changed)

        self.scales = coord_bars
        self.bars_container.add_widget(self.app.servo)

        # Add placeholder widgets for scales
        for _ in range(len(self.app.scales), 4):
            self.bars_container.add_widget(PlaceholderWidget())

        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.exit_stack = ExitStack()
        self.app.bind(current_mode=self.change_mode)
        # When the application starts we restore the last selected mode
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
            
    def on_scale_axis_name_changed(self, scale, axis_name):
        """Handle changes to the axisName property of a scale"""
        if axis_name.strip():
            # If the axis name becomes non-empty and there's a placeholder
            if scale in self.scale_placeholders:
                placeholder = self.scale_placeholders.pop(scale)
                index = self.bars_container.children.index(placeholder)
                self.bars_container.remove_widget(placeholder)
                # Kivy's children are in reverse order, so we need to adjust the index
                self.bars_container.add_widget(scale, index=index)
                if scale not in self.scales:
                    self.scales.append(scale)
        else:
            # If the axis name becomes empty and there's no placeholder
            if scale not in self.scale_placeholders and scale in self.scales:
                self.scales.remove(scale)
                index = self.bars_container.children.index(scale)
                self.bars_container.remove_widget(scale)
                placeholder = PlaceholderWidget()
                # Kivy's children are in reverse order, so we use the same index
                self.bars_container.add_widget(placeholder, index=index)
                self.scale_placeholders[scale] = placeholder
