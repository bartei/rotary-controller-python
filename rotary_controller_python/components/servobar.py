import os

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from loguru import  logger as log

current_app = App.get_running_app()
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout):
    def __init__(self, *args, **kv):
        super(ServoBar, self).__init__(**kv)

