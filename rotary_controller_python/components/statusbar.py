import os

from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from loguru import logger as log

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))

if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class StatusBar(BoxLayout):
    cycles = NumericProperty(0)
    fps = NumericProperty(0)
