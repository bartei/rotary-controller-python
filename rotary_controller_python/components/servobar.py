import logging
import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

current_app = App.get_running_app()
log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout):
    from rotary_controller_python.main import ServoData
    servo = ObjectProperty(rebind=True, defaultvalue=ServoData())

    def __init__(self, *args, **kv):
        super(ServoBar, self).__init__(**kv)

