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
    interval = NumericProperty(0)
    cycles = NumericProperty(0)
    fps = NumericProperty(0)

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        self.app.bind(update_tick=self.update_tick)

    def update_tick(self, *args, **kv):
        self.fps = Clock.get_fps()
        self.interval = self.app.fast_data_values['executionInterval']
        self.cycles = self.app.fast_data_values['cycles']
