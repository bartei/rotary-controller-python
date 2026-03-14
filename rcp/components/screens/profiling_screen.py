from kivy.logger import Logger
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ProfilingScreen(Screen):
    pass