import logging
import os
from decimal import Decimal

from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout


log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Synchro(BoxLayout):
    pass
