from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class RectPopup(Popup):
    ref = ObjectProperty(None)

    def show(self):
        self.open()

    def cancel(self):
        self.dismiss()
