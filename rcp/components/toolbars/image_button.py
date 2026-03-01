from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.button import Button

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ImageButton(Button):
    source = StringProperty("pictures/half-icon-white.png")
