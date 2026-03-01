from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from rcp.dispatchers.circle_pattern import CirclePatternDispatcher
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class CirclePopup(Popup):
    ref = ObjectProperty(None)

    def show(self):
        self.open()

    def on_data(self, instance, value):
        if self.ref is not None:
            self.ref.circle_pattern.origin_x = self.data.origin_x

    def cancel(self):
        self.dismiss()
