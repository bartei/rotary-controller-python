from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ScreenHeader(BoxLayout):
    pass