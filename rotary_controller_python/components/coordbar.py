import logging
import os
import time
import collections

from decimal import Decimal

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from rotary_controller_python.components.appsettings import config

log = logging.getLogger(__file__)
app = App.get_running_app()
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout):
    formatted_axis_speed = NumericProperty(0.000)

    from rotary_controller_python.main import classes
    data = ObjectProperty(rebind=True, defaultvalue=classes[0]())

    def __init__(self, *args, **kv):
        super(CoordBar, self).__init__(**kv)
        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        Clock.schedule_interval(self.update_speed, 1.0 / 10)

    def update_speed(self, *args, **kv):
        current_time = time.time()

        # Calculate axis speed
        self.speed_history.append(
            (Decimal(self.data.position) - self.previous_axis_pos) /
            Decimal(current_time - self.previous_axis_time)
        )

        average = (sum(self.speed_history) / Decimal(len(self.speed_history)))

        if app.current_units == "in":
            # Speed in feet per minute
            self.formatted_axis_speed = float(average * 60 / Decimal("25.4") / 12)
        else:
            # Speed in mt/minute
            self.formatted_axis_speed = float(average * 60 / 1000)

        self.previous_axis_time = current_time
        self.previous_axis_pos = Decimal(self.data.position)
