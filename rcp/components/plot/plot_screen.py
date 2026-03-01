from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class PlotScreen(Screen):
    toolbar = ObjectProperty()
    float_view = ObjectProperty()

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        self.app.beep()
        return super().on_touch_down(touch)

