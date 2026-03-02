from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


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

    def update(self, *args, **kv):
        self.fps = Clock.get_fps()
        if not self.app.board.connected:
            return

        if self.app.board.fast_data_values is None:
            # There is no connection yet
            return
        try:
            self.interval = self.app.board.fast_data_values['executionInterval']
            self.cycles = self.app.board.fast_data_values['cycles']
        except Exception as e:
            log.debug(str(e), exc_info=True)
