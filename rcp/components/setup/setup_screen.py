import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.screenmanager import Screen


log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

class SetupScreen(Screen):
    pass
