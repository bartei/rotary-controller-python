import logging
import os
import time
import collections

from decimal import Decimal

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ConfigParserProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from components.appsettings import config


log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class RotaryBar(BoxLayout):
    input_name = StringProperty()
    desired_position = NumericProperty()
    divisions = NumericProperty()
    division_index = NumericProperty()
    division_offset = NumericProperty()
    display_color = ConfigParserProperty(
        defaultvalue="#ffffffff",
        section="formatting",
        key="display_color",
        config=config
    )

    def update_desired_position(self, *args, **kwargs):
        self.desired_position = 360 / self.divisions * self.division_index + self.division_offset
        return True

    def __init__(self, *args, **kv):
        super(RotaryBar, self).__init__(**kv)
        self.bind(divisions=self.update_desired_position)
        self.bind(division_index=self.update_desired_position)
        self.bind(division_offset=self.update_desired_position)