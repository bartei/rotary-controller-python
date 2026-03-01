from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class TitleItem(BoxLayout):
    name = StringProperty("")
    valign = StringProperty("center")
    halign = StringProperty("center")
