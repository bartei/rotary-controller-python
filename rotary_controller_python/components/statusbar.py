import os

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
    speed = NumericProperty(0)
    maxSpeed = NumericProperty(0)
