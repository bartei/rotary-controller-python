import logging
import os
import time
import collections

from decimal import Decimal

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ConfigParserProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from components.appsettings import config

current_app = App.get_running_app()
log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout):
    from main import ServoData
    servo = ObjectProperty(rebind=True, defaultvalue=ServoData())

    def __init__(self, *args, **kv):
        super(ServoBar, self).__init__(**kv)

