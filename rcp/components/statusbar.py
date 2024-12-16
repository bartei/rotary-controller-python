import os

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))

if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class StatusBar(BoxLayout):
    update_tick = NumericProperty(0)
    interval = NumericProperty(0)
    cycles = NumericProperty(0)
    fps = NumericProperty(0)

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        Clock.schedule_interval(self.update, 1.0 / 5)

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

