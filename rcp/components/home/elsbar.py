import os
from fractions import Fraction

from kivy.app import App
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from pydantic import BaseModel

from rcp.components.home.coordbar import CoordBar
from rcp import feeds
from rcp.dispatchers import SavingDispatcher


class FeedMode(BaseModel):
    id: int
    name: str

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ElsBar(BoxLayout, SavingDispatcher):
    feed_button = ObjectProperty(None)
    feed_ratio = ObjectProperty(None)

    mode_name = StringProperty(":(")
    feed_name = StringProperty(":(")
    current_feeds_index = NumericProperty(0)

    _skip_save = [
        "position",
        "x", "y",
        "minimum_width",
        "minimum_height",
        "width", "height",
    ]

    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        super().__init__(**kwargs)
        if not self.mode_name in feeds.table.keys():
            self.mode_name = feeds.table.keys()[0]
        self.current_feeds_table = feeds.table[self.mode_name]
        self.bind(current_feeds_index=self.update_feeds_ratio)

    def update_current_position(self):
        Factory.Keypad().show_with_callback(self.servo.set_current_position, self.servo.scaledPosition)

    def set_feed_ratio(self, table_name, index):
        table_instance = feeds.table[table_name]
        self.mode_name = table_name
        self.current_feeds_table = table_instance
        self.current_feeds_index = index

    def update_feeds_ratio(self, instance, value):
        ratio = self.current_feeds_table[self.current_feeds_index].ratio
        spindle_scale: CoordBar = self.app.get_spindle_scale()
        if spindle_scale is not None:
            spindle_scale.syncRatioNum = ratio.numerator
            spindle_scale.syncRatioDen = ratio.denominator
        self.feed_name = self.current_feeds_table[self.current_feeds_index].name
        log.info(f"Configured ratio is: {ratio.numerator}/{ratio.denominator}")

    def next_feed(self):
        if self.current_feeds_index < len(self.current_feeds_table) -1:
            self.current_feeds_index = (self.current_feeds_index + 1)

    def previous_feed(self):
        if self.current_feeds_index > 0:
            self.current_feeds_index = (self.current_feeds_index - 1)