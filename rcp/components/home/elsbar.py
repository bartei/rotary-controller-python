import os

from kivy.factory import Factory
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from pydantic import BaseModel


class FeedMode(BaseModel):
    id: int
    name: str


FEED_MODES = [
    FeedMode(id=1, name="Feed\nMM"),
    FeedMode(id=2, name="Feed\nIN"),
    FeedMode(id=3, name="Thread\nMM"),
    FeedMode(id=4, name="Thread\nIN"),
]

def get_feed_mode_by_id(feed_id: int) -> FeedMode | None:
    global FEED_MODES
    result = [item for item in FEED_MODES if item.id == feed_id]
    if len(result) == 0:
        return None
    return result[0]

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ElsBar(BoxLayout):
    feed_button = ObjectProperty(None)
    mode = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_feed_mode(mode=1)

    def update_current_position(self):
        Factory.Keypad().show_with_callback(self.servo.set_current_position, self.servo.scaledPosition)

    def set_feed_mode(self, mode):
        feed_mode = get_feed_mode_by_id(mode)
        if feed_mode is None:
            log.error("Received invalid feed mode")
            return

        log.info(f"Setting feed mode to {feed_mode.id} = {feed_mode.name}")
        self.feed_button.text = feed_mode.name
        self.mode = feed_mode.id
