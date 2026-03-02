from kivy.logger import Logger
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv
from rcp.utils.platform import is_raspberry_pi

log = Logger.getChild(__name__)
load_kv(__file__)


class LogsScreen(Screen):
    is_pi = BooleanProperty(False)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.is_pi = is_raspberry_pi()