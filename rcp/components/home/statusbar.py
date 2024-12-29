from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.components.toolbars.led_button import LedButton

log = Logger.getChild(__name__)


class StatusBar(BoxLayout):
    update_tick = NumericProperty(0)
    interval = NumericProperty(0)
    cycles = NumericProperty(0)
    fps = NumericProperty(0)

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)
        Clock.schedule_interval(self.update, 1.0 / 5)
        self.size_hint = (1, None)
        self.height = 32
        self.orientation = "horizontal"
        com_led = LedButton(
            size_hint_x=None,
            width=64,
            label="COM"
        )
        self.add_widget(com_led)

        # Bind app.connected and app.blink to update led_button.checkbox_value
        def update_checkbox_value(*_):
            com_led.checkbox_value = self.app.connected or self.app.blink

        # Perform the initial update and bind the properties
        update_checkbox_value()
        self.app.bind(connected=update_checkbox_value, blink=update_checkbox_value)

        interval_led = LedButton(
            size_hint_x=None,
            width=64,
            label=""
        )
        self.add_widget(interval_led)
        def update_interval(*_):
            interval_led.label = "{:0.0f}".format(0 if self.interval == 0 else (100000000 / self.interval))
        update_interval()
        self.bind(interval=update_interval)

        fps_led = LedButton(
            size_hint_x=None,
            width=64,
            label=""
        )
        self.add_widget(fps_led)
        def update_fps(*_):
            fps_led.label = str(int(self.fps))
        update_fps()
        self.bind(fps=update_fps)

        cycles_led = LedButton(
            size_hint_x=None,
            width=64,
            label=""
        )
        self.add_widget(cycles_led)
        def update_cycles(*_):
            cycles_led.label = str(int(self.cycles))
        update_cycles()
        self.bind(cycles=update_cycles)

    def update(self, *args, **kv):
        self.fps = Clock.get_fps()
        if not self.app.connected:
            return

        if self.app.fast_data_values is None:
            # There is no connection yet
            return
        try:
            self.interval = self.app.fast_data_values['executionInterval']
            self.cycles = self.app.fast_data_values['cycles']
        except Exception as e:
            log.debug(e.__str__(), exc_info=True)
