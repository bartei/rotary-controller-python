import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ScaleScreen(Screen):
    scale = ObjectProperty()

    # def __init__(self, **kv):
    #     super().__init__(**kv)
    #     self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))